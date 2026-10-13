## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Define Spring beans using Java code, with `@Configuration` and `@Bean`
- Create an application context from a Java configuration class and access beans inside it
- Explain the two equivalent ways to inject one bean's dependency into another within Java config
- Explain why Spring initializes beans eagerly, in dependency order
- Use `ApplicationContext.getBean(...)` in its different forms to retrieve beans programmatically

## Configuration styles in Spring

Spring supports several configuration styles. This module focuses on **Java configuration** — defining bean definitions in regular Java classes, entirely in Java. You'll create an application context from that configuration, access beans inside it, and see how to split configuration across multiple files as an application grows. Along the way you'll also touch on how Spring handles dependencies between beans, and briefly on bean scopes.

## Quick start: your application classes

Everything starts with your application classes — plain POJOs containing just your business logic. You write these; Spring doesn't need you to implement any framework interface or extend any framework class.

```java
public class TransferServiceImpl implements TransferService {
    public TransferServiceImpl(AccountRepository ar) {
        this.accountRepository = ar;
    }
    // Dependency: Needed to perform money transfers between accounts
    ...
}

public class JdbcAccountRepository implements AccountRepository {
    public JdbcAccountRepository(DataSource ds) {
        this.dataSource = ds;
    }
    // Dependency: Needed to access account data in the database
    ...
}
```

Notice again that `TransferServiceImpl` depends on an interface (`AccountRepository`), not on `JdbcAccountRepository` directly — no `new` operator, no service locator. You don't strictly have to depend on interfaces in your classes, but it's good Java practice, since it encourages loose coupling.

The container needs to be told how to construct these POJOs, what their dependencies are, and how they should be initialized. Those instructions are the **configuration** — in this lesson, written in Java.

## How the DI container works, conceptually

![How Spring DI Container Works](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/03-java-configuration/01-spring-quick-start/images/lesson7-how-di-container-works.png)

Your application classes (POJOs) don't wire themselves together. Instead, you supply **configuration metadata**, and the Spring DI container — the `ApplicationContext` — reads that metadata and uses it to construct and wire up your objects. With that metadata in place, the application context eagerly initializes every bean it knows about, so that by the time it's finished starting up, you have a fully configured system ready to use.

## Writing the configuration class: method invocation

A configuration class is a plain Java class, annotated with `@Configuration`, telling the framework it contains bean definitions:

```java
@Configuration
public class ApplicationConfig {

    @Bean
    public TransferService transferService() {
        return new TransferServiceImpl(accountRepository());
    }

    @Bean
    public AccountRepository accountRepository() {
        return new JdbcAccountRepository(dataSource());
    }

    @Bean
    public DataSource dataSource() {
        BasicDataSource dataSource = new BasicDataSource();
        dataSource.setDriverClassName("org.postgresql.Driver");
        dataSource.setUrl("jdbc:postgresql://localhost/transfer");
        dataSource.setUsername("transfer-app");
        dataSource.setPassword("secret45");
        return dataSource;
    }
}
```

Each method annotated with `@Bean` tells Spring it defines a bean in the application context, and acts like a factory method: it contains the initialization logic for that bean and returns the finished object.

- `dataSource()` has no dependencies — it just builds and configures a `DataSource` directly, using hard-coded connection properties.
- `accountRepository()` calls `dataSource()` directly to obtain its dependency. This is called a **cross-reference method invocation** — you're injecting whatever that other `@Bean` method produces, which is a form of injection available in Java configuration.
- `transferService()` uses the same pattern, calling `accountRepository()` to obtain its dependency.

By convention, the **name of the method becomes the name of the bean** unless you override it inside the `@Bean` annotation. Also notice that `accountRepository()` returns the `AccountRepository` interface type, not the concrete `JdbcAccountRepository` — keeping the same interface-based decoupling from earlier lessons.

## An equivalent alternative: dependencies as method arguments

Instead of calling another `@Bean` method directly, you can declare the dependency as a method argument, and let Spring supply it:

```java
@Configuration
public class ApplicationConfig {

    @Bean
    public TransferService transferService(AccountRepository repository) {
        return new TransferServiceImpl(repository);
    }

    @Bean
    public AccountRepository accountRepository(DataSource dataSource) {
        return new JdbcAccountRepository(dataSource);
    }

    @Bean
    public DataSource dataSource() {
        BasicDataSource dataSource = new BasicDataSource();
        ...
        return dataSource;
    }
}
```

Here, `accountRepository(...)` simply declares that it needs a `DataSource` argument, and Spring finds the matching bean in the application context and supplies it — there's a bean of type `DataSource` available, so it gets passed in automatically. The same applies to `transferService(...)` and its `AccountRepository` argument. Both approaches — cross-reference method invocation, or dependencies as method arguments — are equivalent; which one you use is a matter of style.

## Creating the application context

With your business logic and configuration class written, the next step is to actually create the application context:

```java
// Create application context from the configuration
ApplicationContext context = SpringApplication.run(ApplicationConfig.class);

// Look up a bean from the application context
TransferService service = context.getBean("transferService", TransferService.class);

// Use the bean
service.transfer(new MonetaryAmount("300.00"), "1", "2");
```

`SpringApplication` is technically a Spring Boot class, but it's being used here purely as a convenient way to create the application context — this course is not using Spring Boot's auto-configuration. Passing in `ApplicationConfig.class` tells it which configuration to use to define beans; the context then eagerly creates every bean declared in that class.

Once you have the context, `context.getBean(...)` retrieves a fully wired bean — here, a bean named `"transferService"` of type `TransferService`. Because it's already been assembled by the container, it comes back fully wired: its repository is set, and that repository's own `DataSource` is set too. This is your application's entry point — it is *not* a service locator pattern; you use it once, at startup, to obtain your top-level bean, and then call its business methods directly (like `transfer(...)` here).

Also worth remembering: Spring will create *four* beans from this configuration class, not three — `ApplicationConfig` itself is also registered as a Spring bean.

## Accessing beans programmatically: three flavors

There's more than one way to call `getBean(...)`:

```java
ApplicationContext context = SpringApplication.run(...);

// Use bean id, a cast is needed
TransferService ts1 = (TransferService) context.getBean("transferService");

// Use typed method to avoid casting
TransferService ts2 = context.getBean("transferService", TransferService.class);

// No need for bean id if type is unique - recommended (use type whenever possible)
TransferService ts3 = context.getBean(TransferService.class);
```

- **By name only** — `getBean("transferService")` returns a plain `Object`, so you need to cast it yourself; this is the least type-safe option.
- **By name and type** — `getBean("transferService", TransferService.class)` avoids the cast, since you've told Spring what type to expect.
- **By type only** — `getBean(TransferService.class)` is the most convenient, and is recommended whenever you can use it. It works as long as there's exactly one bean of that type in the context; if there's more than one, this becomes ambiguous, and Spring won't know which one to give you.

## Inside the application context: initialization order

When `SpringApplication.run(...)` builds the context, it initializes every component in the right order, based on their dependencies:

![Inside the Spring Application Context](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/03-java-configuration/01-spring-quick-start/images/lesson7-inside-application-context.png)

Working through this example: `dataSource` has no dependencies, so it's created first. `accountRepository` depends on `dataSource`, which already exists, so it's created next. Finally, `transferService` depends on `accountRepository`, which is now available, so it's created last. Every one of these beans is given a unique id or name (matching the `@Bean` method's name by convention), so from outside the context you can retrieve any of them directly — `getBean("transferService")`, `getBean("accountRepository")`, or `getBean("dataSource")` — and each comes back fully configured and ready to use.

## Recap

- Spring separates application configuration from the application objects (beans) themselves.
- `@Configuration` classes with `@Bean`-annotated factory methods are one way to provide that configuration, entirely in Java.
- Dependencies between beans can be expressed either as a direct cross-reference method invocation, or as method arguments that Spring resolves for you — the two are equivalent.
- Spring manages your application objects: it creates them in the correct dependency order, and ensures they're fully initialized before use.
- Each bean is given a unique id/name, and can be retrieved from the context by name, by name and type, or by type alone.

## Check your understanding

1. In a `@Configuration` class, what are the two equivalent ways to inject one bean's dependency into another `@Bean` method?
2. Given `dataSource()`, `accountRepository(DataSource)`, and `transferService(AccountRepository)` bean methods, in what order will Spring create these three beans, and why?
3. Which form of `getBean(...)` should you prefer when there's only one bean of the type you need, and why?

Next up is **The Application Context**, which looks more closely at creating the application context across different environments.
