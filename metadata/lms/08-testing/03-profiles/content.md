## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Activate one or more Spring profiles inside a test class with `@ActiveProfiles`
- Explain how profile activation interacts with the beans that get loaded into a test's application context
- Assign a profile to a bean either through Java config or through a stereotype annotation like `@Repository`
- Use `@Sql` to run SQL scripts before or after a test method, to set up or tear down test data
- Configure what happens when an `@Sql` script fails

## A quick recap: what a profile is

Earlier in this course you saw how Spring profiles let you group beans so they can be enabled or disabled at runtime — useful for things like swapping a real database for a stub, depending on whether you're running in production or in a test. Normally you'd activate a profile by passing a system property at startup, but that technique doesn't translate well into a test environment, where there's no command line to pass properties to. This lesson introduces the annotation-based way of activating profiles specifically for tests, and pairs it with a second annotation for loading SQL scripts into a test database.

## Activating profiles for a test: \@ActiveProfiles

`@ActiveProfiles` is a new annotation, used in combination with `@SpringJUnitConfig` (or the underlying Spring extension you saw in the earlier testing lessons). It lets you define one or more profiles that should be active for a given test class.

```java
@SpringJUnitConfig(DevConfig.class)
@ActiveProfiles({"jdbc", "dev"})
public class TransferServiceTests { ... }
```

When Spring creates the application context for this test class, it takes the active profiles into account: it creates every bean that doesn't belong to any profile, plus every bean that belongs to one of the profiles you activated. Beans tied to a profile you *didn't* activate are simply skipped. Remember from the earlier testing lessons that this application context is shared and cached across test methods in the same class — the profiles you activate apply to that whole shared context.

## Assigning a bean to a profile

You can define which profile a bean belongs to in either Java config or annotation-based configuration — the two configuration styles you've used throughout this course.

**Java config**: put `@Profile` on the `@Configuration` class itself (making every bean in that class belong to the profile), or on an individual `@Bean` method.

```java
@Configuration
@Profile("jdbc")
public class DevConfig {

    @Bean
    public ... jdbcAccountRepository() { ... }
}
```

**Annotation-based configuration**: put `@Profile` directly on the component class, typically combined with a stereotype annotation like `@Repository` or `@Controller`.

```java
@Repository
@Profile("jdbc")
public class JdbcAccountRepository { ... }
```

Either way, the rule is the same: when you activate a profile in your test with `@ActiveProfiles`, Spring only instantiates beans matching that profile (or belonging to no profile at all) — beans tied to a profile you haven't activated are left out of the application context entirely.

## Testing with databases

Integration testing against a real SQL database is common, and in-memory (embedded) databases are especially useful for this kind of testing since they require no prior installation. A common requirement when doing this is to populate the database with data before each test runs — and Spring's testing support has a dedicated annotation for exactly that: `@Sql`.

```java
@Test
@Sql("/testfiles/test-data.sql")
public void successfulTransfer() {
    ...
}
```

Annotating a test method with `@Sql` and pointing it at a script tells Spring to run that script against the data source before the annotated test method executes — a convenient way to load exactly the data a given test needs.

## Using \@Sql at the class level, and overriding it per test

`@Sql` can also be placed on the class itself, in which case it applies to every test method in that class unless a specific method overrides it with its own `@Sql` annotation.

```java
@SpringJUnitConfig(...)
@Sql({"/testfiles/schema.sql", "/testfiles/load-data.sql"})
public class MainTests {

    // schema.sql and load-data.sql only run before this test
    @Test
    public void success() { ... }

    @Test // Overrides to use own scripts
    @Sql(scripts = "/testfiles/setupBadTransfer.sql")
    @Sql(scripts = "/testfiles/cleanup.sql",
         executionPhase = Sql.ExecutionPhase.AFTER_TEST_METHOD)
    public void transferError() { ... }
}
```

In this example, `schema.sql` and `load-data.sql` run before every test in the class — except `transferError`, which defines its own pair of `@Sql` annotations instead. Notice that `@Sql` is a *repeatable* annotation: you can stack more than one on the same method. The second annotation on `transferError` also sets `executionPhase` to run its script *after* the test method — a handy way to clean up test data once a test finishes, rather than (or in addition to) setting it up beforehand.

## \@Sql options

`@Sql` has quite a few configuration options beyond just which script to run:

- **`executionPhase`** — run the script before the test method (the default) or after it.
- **`config`** — a nested `@SqlConfig` for controlling how the script is interpreted, including:
  - **What to do if the script fails**: `FAIL_ON_ERROR` (the default), `CONTINUE_ON_ERROR`, `IGNORE_FAILED_DROPS`, or `DEFAULT` (whatever `@Sql` defines at the class level, otherwise `FAIL_ON_ERROR`).
  - SQL syntax control, such as the comment prefix and statement separator your script uses.

```java
@Sql(scripts = "/test-user-data.sql",
     config = @SqlConfig(errorMode = ErrorMode.FAIL_ON_ERROR,
                          commentPrefix = "//", separator = "@@"))
```

By default, `@Sql` looks up a `DataSource` bean in the application context and runs its scripts against it. There's more to configure here — including how transactions and a custom transaction manager interact with `@Sql` — but that's revisited in a later module once transaction management itself has been introduced.

The next lesson puts profiles and `@Sql` into practice together in a hands-on lab.
