## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Distinguish unit testing from integration testing, and explain what changes between production and test infrastructure
- Use `@ExtendWith(SpringExtension.class)` and `@ContextConfiguration` (or the combined `@SpringJUnitConfig`) to bootstrap a real application context inside a JUnit 5 test
- Autowire dependencies into a test class at the field level or the method-argument level
- Override configuration for a single test using an embedded static configuration class
- Control application context caching and reuse with `@DirtiesContext`, and load test-only properties with `@TestPropertySource`

## Unit testing vs. integration testing

There are many kinds of tests — unit, integration, performance, end-to-end, and more. This lesson focuses on integration testing, but it's worth being precise about how it differs from unit testing first.

**Unit testing** doesn't need Spring at all. You're testing a single component in isolation, with dependencies kept to a minimum — and since your components will have real dependencies, you fake them with stubs or mocks rather than integrating with an actual database or messaging system (see the Appendix for more details on stubs and mocks). A unit test is implemented with plain JUnit; Spring doesn't come into it.

**Integration testing** is different: here, you *do* need Spring, because the point is to test several components collaborating together, and Spring is what wires those components together. The infrastructure surrounding your components in a test environment usually isn't the same as production — typically, it's scaled down. If your application needs a servlet container in production, you likely won't spin one up for the test. If it needs a message broker, you might use ActiveMQ instead of a commercial messaging server. If it needs a database, you'll often substitute an embedded database for the real one. Test containers are another option — spinning up a lightweight, throwaway container (a database, a messaging broker, anything that can run in Docker) just for the test, then tearing it down afterward.

## The same business logic, different infrastructure

![Integration Test Example: production mode vs. integration test, side by side](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/08-testing/02-integration/images/lesson30-integration-test-example.png)

In production, your application wires together `TransferServiceImpl` and `JpaAccountRepository`, backed by the production database. In an integration test, you build a test class — `TransferServiceTests` — that wires together the *same* `TransferServiceImpl` and `JpaAccountRepository`, but backed by a test database instead. The business logic under test doesn't change at all; only the infrastructure underneath it does.

## Spring's test context framework

Spring ships a small testing framework called the **`TestContext` framework**, whose job is to bootstrap the application context for you.

Without it, you'd be tempted to create the application context yourself inside a `@BeforeEach` method — but that's wasteful, since it means rebuilding the whole context before every single test method. The `TestContext` framework creates the application context for you instead, based on the **`@ContextConfiguration`** annotation, which you use to point at the configuration class (or classes) you want loaded. All of this comes from the `spring-test` module, so it needs to be on your test classpath (packaged as `spring-test.jar`). See the Spring Framework reference for <a href="https://docs.spring.io/spring/docs/current/spring-framework-reference/testing.html#integration-testing" target="_blank" rel="noopener noreferrer">integration testing</a> and the <a href="https://docs.spring.io/spring/docs/current/spring-framework-reference/testing.html#testcontext-framework" target="_blank" rel="noopener noreferrer">TestContext framework</a>.

## Hooking Spring into JUnit 5: \@ExtendWith

JUnit 4 had **runners**, but runners came with a real limitation: you couldn't combine more than one at a time, so if two different frameworks each needed their own runner, you were stuck. JUnit 5 replaces that mechanism with **extensions** — and extensions don't have that limitation; you can apply several at once.

Spring provides its own extension point for exactly this purpose: the **`SpringExtension`** class — a Spring-aware test runner for the JUnit 5 world. `@ExtendWith` replaces JUnit 4's `@RunWith`, and its name reflects that JUnit 5 supports multiple extensions. (See the Appendix for Spring's JUnit 4 support.)

Putting it together:

```java
@ExtendWith(SpringExtension.class)
@ContextConfiguration(classes = {SystemTestConfig.class})
public class TransferServiceTests {

    @Autowired
    private TransferService transferService;

    @Test
    public void shouldTransferMoneySuccessfully() {
        TransferConfirmation conf = transferService.transfer(...);
        // Test the system as normal
    }
}
```

`@ExtendWith(SpringExtension.class)` tells JUnit 5 to run the test with Spring support; `@ContextConfiguration` tells Spring which configuration class (or classes) to use to build the application context. Once that context is bootstrapped, `@Autowired` at the field level works exactly as it would in application code — here, injecting the real `TransferService`, which internally delegates down to the repository and, in turn, to whatever `DataSource` the test configuration provides. There's no need for a `@BeforeEach` method to manually construct `TransferService` — the injected bean is ready to test against directly.

## \@SpringJUnitConfig: one annotation instead of two

Because `@ExtendWith(SpringExtension.class)` and `@ContextConfiguration` are almost always used together, Spring provides a single **composed annotation** that combines both: **`@SpringJUnitConfig`**.

```java
@SpringJUnitConfig(SystemTestConfig.class)
public class TransferServiceTests {
    ...
}
```

This is the recommended way to write the class-level annotation going forward — one annotation to remember instead of two, and it still lets you pass the configuration classes directly, the same way `@ContextConfiguration` did.

## Autowiring at the argument level

So far, dependency injection has been shown at the field level, but there's an alternative: autowiring directly on a test method's argument.

```java
@SpringJUnitConfig(SystemTestConfig.class)
public class TransferServiceTests {
    // private TransferService transferService;  // no longer required as a field

    @Test
    public void shouldTransferMoneySuccessfully(@Autowired TransferService transferService) {
        TransferConfirmation conf = transferService.transfer(...);
    }
}
```

Both techniques get you a reference to the same bean from the application context — the difference is really about scope. Field injection makes the dependency available to every test method in the class; argument injection restricts its visibility to just the one test method that declares it. Either is a legitimate choice depending on how widely a given dependency is needed.

## Overriding configuration with an embedded static class

Sometimes a single test needs its own tweak to the configuration — without touching the shared configuration used by every other test. `@SpringJUnitConfig` supports this by looking for an embedded (static, inner) configuration class inside the test class itself:

```java
@SpringJUnitConfig(SystemTestConfig.class)   // Don't specify any config classes explicitly
public class JdbcAccountRepoTest {

    @Test
    public void shouldUpdateDatabaseSuccessfully() { ... }

    @Configuration
    @Import(SystemTestConfig.class)          // Looks for configuration embedded in test class
    static class TestConfig {
        @Bean
        public DataSource dataSource() { ... }   // Override a bean with a test alternative
    }
}
```

The inner `TestConfig` class imports all of `SystemTestConfig`'s beans via `@Import`, but also defines its own `DataSource` bean. Since a bean defined this way takes precedence over one already present from the imported configuration, the `DataSource` gets overridden just for this particular test class — without affecting `SystemTestConfig` itself, or any other test that uses it.

## Application context caching, and \@DirtiesContext

One of the real benefits of `@SpringJUnitConfig` (or the extension plus `@ContextConfiguration` combination underneath it) is that the application context it creates gets **cached**. That means the context — and the beans injected from it — isn't rebuilt before every test method; injection effectively happens once, and the same cached context and bean instances are reused across every test method in the class. Given that most Spring beans are meant to be stateless, immutable singletons, this is normally exactly what you want: there's no need for a fresh context per test.

But if a particular test method *does* deliberately mutate shared state, you don't want that mutated state leaking into the next test, which isn't expecting it. For that case, there's **`@DirtiesContext`**:

```java
@DirtiesContext
@Test
public void testTransferLimitExceeded() {
    transferService.setMaxTransfers(0);
    // ...do a transfer, expect a failure
}
```

Annotating a test method this way forces the cached context to be closed and destroyed once that test finishes, and the next test that needs a context gets a freshly built one instead of the cached one. Be careful reaching for this, though — creating a new application context takes real time, and using `@DirtiesContext` more than necessary will slow your test suite down.

## Test-only properties with \@TestPropertySource

Just as `@PropertySource` lets your application load property files into the environment, `@TestPropertySource` lets a test do the same thing — either by supplying key/value pairs directly, or by pointing at a properties file. If you don't specify a location, it defaults to looking for `[classname].properties`:

```java
@SpringJUnitConfig(SystemTestConfig.class)
@TestPropertySource(properties = {"username=foo", "password=bar"},
                     locations = "classpath:/transfer-test.properties")
public class TransferServiceTests {
    ...
}
```

Properties specified this way have **higher precedence** than sources already present in your application — meaning these test-supplied values will override any matching property your application would otherwise pick up, so the test is guaranteed to see its own values rather than production defaults.

## The benefits, all together

- **No need to deploy to an external container** to test application functionality — everything runs quickly inside your IDE or CI/CD pipeline, which is exactly what supports continuous integration testing.
- **Configuration is reused between test and production environments.** Application-level configuration logic is typically shared; only infrastructure-specific configuration — data sources, JMS queues, and the like — differs by environment.

Scaling down the infrastructure layer this way is what makes it practical to run your test suite anywhere: in your IDE, in your build tool, in CI — without depending on anything external being available.

## Recap

- Unit tests isolate a single component and avoid Spring entirely; integration tests use Spring to wire multiple real components together, typically against scaled-down infrastructure.
- `@ExtendWith(SpringExtension.class)` plugs Spring into JUnit 5's extension model; `@ContextConfiguration` tells it which configuration classes to load; `@SpringJUnitConfig` composes both into one annotation.
- Dependencies can be autowired at the field level (visible to the whole test class) or the method-argument level (visible to just that test method).
- An embedded static `@Configuration` class inside a test class, combined with `@Import`, lets you override a single bean just for that test without touching the shared configuration.
- The application context built for a test class is cached and reused across test methods by default — `@DirtiesContext` forces a rebuild when a test has mutated shared state.
- `@TestPropertySource` loads test-only properties (inline or from a file) with higher precedence than your application's normal property sources.

## Check your understanding

1. What's the practical difference between autowiring a dependency as a test class field versus as a `@Test` method argument?
2. Why does the embedded static configuration class in `JdbcAccountRepoTest` still need `@Import(SystemTestConfig.class)`, rather than just defining its own `DataSource` bean on its own?
3. If a test mutates shared application state and doesn't use `@DirtiesContext`, what's the risk for the next test method that runs?

The next lesson builds on this foundation by looking at how Spring profiles and databases fit into your test configuration.
