## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain the key principles the DI container applies — DRY, separation of concerns, the POJO programming model, and convention over configuration
- Describe the problem dependency injection solves, using a concrete multi-component example
- Explain why depending on interfaces rather than concrete implementations matters
- Explain why decoupling components this way makes unit testing easier

## Why a DI container?

The DI container is the heart of Spring. When you implement an enterprise application, you usually need to provide a lot of infrastructure — and one of Spring's central goals is to let you focus on business logic while Spring does the heavy lifting: all the "plumbing" that infrastructure requires.

Spring achieves this by applying a few key principles, all of which you'll see recur throughout this course:

- **Don't Repeat Yourself (DRY)**
- **Separation of Concerns** — you don't want to mix business logic with security, transactions, or any other cross-cutting concern; each stays separate
- **The POJO programming model** — your classes contain just your business logic, with no dependency on the framework itself. That makes them straightforward to test in isolation, since you're testing pure business logic, not framework wiring.
- **Convention over Configuration** — you'll meet several of Spring's conventions as the course progresses

## A motivating example: transferring money

Very few real applications consist of a single, self-contained component. Usually one component has to delegate to others to get its job done.

![DI Example: Banking Application Configuration](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/02-overview/02-container/images/lesson3-banking-application-configuration.png)

Here, a `TransferService` needs to delegate to a `TransferRepository` and an `AccountRepository` to actually carry out a money transfer.

When `transfer(...)` is called on the `TransferService`, it delegates to the `AccountRepository` to load the first account, delegates again to load the second account, and then debits one account and credits the other. Finally, it has to persist both updated accounts before returning control to whoever called `transfer`.

This raises some real questions:

- How would we configure the application to ensure all components are assembled correctly?
- How can we instantiate `TransferService` and `AccountRepository` objects?
- How can we make the `AccountRepository` object available to the `TransferService` object?
- How can we easily swap out an implementation without re-writing the application?
- How can we make different types of `AccountRepository` objects available to the `TransferService` object?

Traditionally, in plain Java, you'd answer the "how do I get an instance" question with the `new` operator, or with a service locator pattern.

## Letting the container do the assembly

This is exactly the gap the DI container fills. Instead of components reaching out and constructing their own dependencies, the container assembles everything for you.

![Money Transfer System Assembly](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/02-overview/02-container/images/lesson3-money-transfer-system-assembly.png)

The diagram's red box represents the Spring container. It configures both the `TransferServiceImpl` and the `JdbcAccountRepository`, takes care of initializing each one, and wires them together. The equivalent hand-written code would look like this:

```java
// (1) create the repository
AccountRepository repository = new JdbcAccountRepository(...);

// (2) create the service
TransferService service = new TransferServiceImpl();

// (3) inject the repository into the service
service.setAccountRepository(repository);
```

Notice the order: the repository (Part 1) is created first, and only then is the service (Part 2) assembled using it. The container's job is to run through that same sequence for you, based on how your beans depend on each other.

## Why depend on interfaces

If you look at the components themselves, they're just POJOs — they don't have any dependency on the framework.

![Parts are Just Plain Old Java Objects (POJOs)](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/02-overview/02-container/images/lesson3-pojos-code.png)

```java
public class JdbcAccountRepository implements AccountRepository {
    ...
}

public class TransferServiceImpl implements TransferService {
    private AccountRepository accountRepository;

    public void setAccountRepository(AccountRepository ar) {
        accountRepository = ar;
    }
    ...
}
```

`JdbcAccountRepository` implements an interface — but it's *our own* business interface, not a framework interface. And critically, `TransferServiceImpl` depends on the `AccountRepository` interface, not on `JdbcAccountRepository` directly. This is one of the main reasons to use dependency injection in the first place: it decouples the two components. `TransferServiceImpl` doesn't know or care whether it's been handed an in-memory repository, a JDBC-backed one, or a JPA-backed one — it just knows it needs *something* that satisfies `AccountRepository`, and it exposes a setter so that dependency can be supplied from the outside.

## Swapping implementations

Because the service only depends on the interface, changing the underlying implementation is simple — you don't touch `TransferServiceImpl` at all, you just re-implement (or add a new implementation of) `AccountRepository`.

![Swapping Out Part Implementations](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/02-overview/02-container/images/lesson3-swapping-implementations-jpa.png)

```java
// (1) swap in a different repository implementation
AccountRepository repository = new JpaAccountRepository(...);
TransferService service = new TransferServiceImpl();
service.setAccountRepository(repository);
```

The DI container creates the `JpaAccountRepository`, creates the `TransferServiceImpl`, and injects the former into the latter — `TransferServiceImpl` is never aware of which concrete implementation it received.

## Why this matters for testing

This decoupling pays off directly in unit tests. When you're writing a unit test, there's no Spring container involved at all — you create your own stub or mock and inject it directly:

```java
AccountRepository stubRepository = new StubAccountRepository();
TransferService service = new TransferServiceImpl();
service.setAccountRepository(stubRepository);
```

Because `TransferServiceImpl` never depended on a concrete repository type, substituting a test stub for the real implementation requires no changes to the service code at all.

Next up is **Spring Framework History**, which looks at how Spring became so popular and where it's headed.
