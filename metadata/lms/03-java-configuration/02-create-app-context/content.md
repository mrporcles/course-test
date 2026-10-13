## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain what the application context actually is and why it's central to everything in Spring
- List the different kinds of environments an application context can be created in
- Bootstrap an application context explicitly inside a JUnit test using `SpringApplication.run`
- Look up a bean from the context with `getBean` and use it in a test

## The application context is the heart of Spring

Recall from the "Quick Start with Java Configuration" lesson that Java-based configuration classes are just recipes: they describe *what* beans exist and how they depend on each other, but they don't do anything by themselves. Something has to read those recipes, create the beans, wire up their dependencies, and keep track of the result. That "something" is the **application context** — the Spring dependency injection (DI) container.

The application context takes care of the entire lifecycle of your components: creating them, injecting their dependencies, and handing them out whenever something asks for them by type or by name.

A natural question follows: where can you actually create this application context? The answer is that you can create it in pretty much any environment:

- A standalone application (a plain `main` method)
- A web application
- A test environment (a JUnit test)

This lesson focuses on the last of these, because it's the most immediately useful for verifying that your configuration actually works.

## Bootstrapping the context inside a test

The example used throughout this lesson is a `TransferServiceTests` class. This training uses JUnit 5 throughout, so the annotations you'll see are the JUnit 5 ones — if you've used JUnit 4 or TestNG before, the same ideas apply, just with different annotation names.

```java
public class TransferServiceTests {
    private TransferService service;

    @BeforeEach
    public void setUp() {
        // Create application context from the configuration
        ApplicationContext context = SpringApplication.run(ApplicationConfig.class);

        // Look up a service
        service = context.getBean(TransferService.class);
    }

    @Test
    public void moneyTransfer() {
        Confirmation receipt = service.transfer(new MonetaryAmount("300.00"), "1", "2");

        Assert.assertEquals("500.00", receipt.getNewBalance());
    }
}
```

Walking through what's happening here:

- **`@BeforeEach`** is a JUnit 5 annotation meaning "run this method before every single test in this class." That makes it exactly the right place to bootstrap the context, since most tests in the class will want a freshly created one.
- **`SpringApplication.run(ApplicationConfig.class)`** is the call that actually creates the application context. You pass it your configuration class — the same kind of `@Configuration` class from the "Quick Start with Java Configuration" lesson — and it builds the context: initializing every bean, injecting every dependency, everything.
- **`context.getBean(TransferService.class)`** looks up a bean by its type. This doesn't return some half-built stub — it returns the `TransferService` fully configured, with its repository already injected, and that repository itself already wired up with its data source. Getting one bean from a fully-built context means the *entire* dependency graph behind it is already in place.
- The result is stored in a private field so the test method below can use it.

The test method itself, `moneyTransfer`, is plain business logic: it calls `service.transfer(...)`, moving 300 euros from one account to another. Because this is a test, you have full control over the starting data — the balance is known to have started at 200, so after transferring 300 more, the assertion checks that the new balance comes out to 500.

That's the whole pattern: build the context once per test, pull out the bean you need, and exercise it like any other object.

## A caveat: this is the explicit way

Everything above creates the application context **explicitly** — you're calling `SpringApplication.run` yourself, by hand, inside `@BeforeEach`. That's worth understanding because it shows you exactly what's happening under the hood, but it isn't necessarily the best way to write a real test suite.

Later in the course, you'll see how Spring's test context framework can do this **implicitly** for you — meaning you write far less boilerplate, and the framework takes care of building (and, importantly, reusing) the context across tests. For now, it's enough to know that this manual, explicit approach exists and works correctly; the more convenient version is coming.

## Recap

- The application context is Spring's DI container — it manages the full lifecycle of your beans.
- It can be created in any environment: standalone applications, web applications, or tests.
- `SpringApplication.run(SomeConfig.class)` builds the context from a configuration class.
- `context.getBean(SomeType.class)` retrieves a fully wired bean, with its entire dependency graph already resolved.
- This explicit, manual approach works, but Spring's test context framework offers a more convenient, implicit alternative you'll meet later in the course.

## Check your understanding

1. What does `SpringApplication.run` actually return, and what has already happened to every bean inside it by the time it returns?
2. Why does creating the context inside a `@BeforeEach` method make sense for a test class with multiple `@Test` methods?
3. What's the practical difference between the explicit approach shown in this lesson and the "implicit" approach mentioned at the end?

So far, every example has used a single configuration file. The next lesson looks at what happens — and what good practice looks like — once your configuration needs to be split across multiple files.
