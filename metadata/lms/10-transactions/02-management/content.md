## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain the two-step process for enabling declarative transaction management in Spring
- Declare a `PlatformTransactionManager` bean for a given technology, such as JDBC
- Annotate a method or class with `@Transactional` to mark it as a transaction boundary
- Explain how the Spring proxy and `PlatformTransactionManager` cooperate to begin, commit, or roll back a transaction
- Combine class-level and method-level `@Transactional` settings, and avoid the common mistake of importing the wrong `@Transactional` annotation

## Separating *where* from *how*

the "Why Transactions and how Java supports them" lesson established why transactions matter; this lesson covers how Spring actually implements them. The central idea is a clean separation of concerns: your code declares **where** transaction boundaries belong, and Spring's configuration decides **how** that transaction is actually implemented underneath.

Concretely:

- Transaction **demarcation** — deciding which methods should run inside a transaction — is expressed **declaratively**, via AOP (a programmatic approach is also available, but this module sticks to the declarative style).
- Transaction **implementation** is hidden behind the `PlatformTransactionManager` abstraction, which has several concrete implementations depending on the technology in use.

Because your business code only ever depends on the abstraction, switching from a local transaction to a global (distributed) one is a small, configuration-only change — you're not rewriting business logic, just swapping which `PlatformTransactionManager` implementation is wired up.

## The two steps

Enabling Spring's declarative transaction management comes down to exactly two steps:

1. **Declare a `PlatformTransactionManager` bean** in the application context.
2. **Declare the transactional methods** — using annotations (recommended) or the programmatic approach; the two can even be mixed and matched.

You'll also need `@EnableTransactionManagement` on a configuration class, which registers the Spring components that actually power the annotation-driven approach.

## Step 1: `PlatformTransactionManager` implementations

`PlatformTransactionManager` is the base interface — the abstraction mentioned above — and Spring ships several implementations, each suited to a different technology:

- **`DataSourceTransactionManager`** — for plain JDBC (and technologies like MyBatis that sit on top of it)
- **`JmsTransactionManager`** — for JMS
- **`JpaTransactionManager`** — for JPA
- **`JtaTransactionManager`** (generic) plus container-specific variants like the WebLogic and WebSphere transaction managers, for JTA

This module focuses on **local** transaction management rather than JTA. Spring itself doesn't provide a JTA implementation — using JTA means either relying on a full application server or bringing in a standalone JTA implementation, which is outside this module's scope.

Declaring the bean is exactly like declaring any other Spring bean — configure it appropriately for your technology and target `DataSource`:

```java
@Bean
public PlatformTransactionManager transactionManager(DataSource dataSource) {
    return new DataSourceTransactionManager(dataSource);
}
```

Note that this bean depends on a `DataSource` already being defined elsewhere in the application context — the transaction manager doesn't create one itself. The recommended bean id for this bean is `transactionManager`.

(The JTA equivalent looks similar in shape but does a JNDI lookup to obtain the `DataSource` from an application server, and constructs a `JtaTransactionManager` instead — again, not the focus here.)

## Step 2: \@Transactional

With a transaction manager in the application context, the next step is marking which methods should actually run inside a transaction, using the `@Transactional` annotation:

```java
public class RewardNetworkImpl implements RewardNetwork {
    @Transactional
    public RewardConfirmation rewardAccountFor(Dining d) {
        // atomic unit-of-work
    }
}
```

This defines `rewardAccountFor` as transactional — but remember, annotations by themselves are just labels; something still needs to process them. That's exactly what `@EnableTransactionManagement` does in your configuration: it activates the bean post-processors responsible for building **proxies** around your annotated components, since Spring AOP relies on proxies to layer additional behavior on top of your existing business logic.

## How it works underneath: the proxy

Here's the mechanism in full:

![Declarative Transaction Management: the target service is wrapped in a Spring proxy, which uses a Spring TransactionInterceptor to begin and commit around calls to the target](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/10-transactions/02-management/images/lesson39-declarative-transaction-management-proxy.png)

Your actual implementation — say, `TransferServiceImpl` — gets wrapped inside a **Spring proxy** at runtime, built by a bean post-processor. The caller is injected with a reference to that *proxy*, not the raw target object. Inside the proxy sits a **Spring `TransactionInterceptor`**, using an "around" advice — meaning it runs code both before and after the actual business logic.

So when a caller invokes something like `transfer("$50", "1", "2")`:

1. The call goes through the proxy first, and is intercepted by the `TransactionInterceptor`.
2. The interceptor delegates to the `PlatformTransactionManager` already sitting in the application context, which **begins** the transaction.
3. Control passes to the real target (`TransferServiceImpl`), which runs the actual business logic — by default, everything that method does runs inside that transaction.
4. Control returns to the interceptor, which delegates to the transaction manager again — this time to **commit** (or roll back) the transaction.
5. Finally, control returns to the original caller.

In short: transaction management behavior is added *around* your code, without your business logic needing to know anything about transactions directly.

## What happens on success vs. failure

The interceptor's around-advice logic follows a specific default rule:

- If the target method runs to completion with no exception, the transaction **commits**.
- If the target method throws a **runtime (unchecked) exception**, the transaction **rolls back**. This is the common case, since Spring APIs generally throw unchecked exceptions (recall the "Exception Handling" lesson's `DataAccessException` hierarchy).
- If the target method throws a **checked exception** from some third-party library, the default behavior is that the transaction still **commits** — which can be surprising. This default can be overridden through configuration, and overriding rollback rules is covered in a later lesson.

## Transactions are bound to the current thread

Once a transaction is under way, Spring binds its transactional context to the **current thread**, using a thread-local variable. That means any component running on that same thread can access the current transactional context — which is exactly the mechanism the `JdbcTemplate` you've been using relies on:

- `JdbcTemplate`, used inside an `@Transactional` method, automatically checks the thread-local for a current connection — if one exists, it reuses it and participates in the same transaction, rather than opening a new one. (Hibernate sessions and JTA work the same way for their respective technologies.)
- You *can* access this manually via `DataSourceUtils.getConnection(dataSource)`, which returns the thread-bound connection if one exists, or falls back to getting one from the `DataSource` otherwise — but you'll rarely need to reach for this yourself, since Spring handles it for you underneath `@Transactional`.

## Combining class-level and method-level \@Transactional

`@Transactional` can be placed on an entire class (or interface, since Spring Framework 5), which makes every method in that class transactional and inherits whatever settings are defined at the class level:

```java
@Transactional
public class RewardNetworkImpl implements RewardNetwork {
    public RewardConfirmation rewardAccountFor(Dining d) {
        // atomic unit-of-work
    }
    public RewardConfirmation updateConfirmation(RewardConfirmation rc) {
        // atomic unit-of-work
    }
}
```

Individual methods can override specific properties from the class-level default:

```java
@Transactional(timeout = 60)
public class RewardNetworkImpl implements RewardNetwork {

    public RewardConfirmation rewardAccountFor(Dining d) {
        // atomic unit-of-work
    }

    @Transactional(timeout = 45)
    public RewardConfirmation updateConfirmation(RewardConfirmation rc) {
        // atomic unit-of-work
    }
}
```

Here, the class-level default gives every method a 60-second timeout. `updateConfirmation` overrides that specifically to 45 seconds, while `rewardAccountFor` keeps the class-level default of 60.

## A common trap: two different \@Transactional annotations

There are actually **two** `@Transactional` annotations available on the classpath: one in `jakarta.transaction` (the standard JTA version — `javax.transaction` on Spring Framework 5.x and earlier) and one in Spring's own package. If you import the standard JTA `@Transactional`, you'll find you can't override properties like propagation, since that version simply doesn't expose them. Always make sure you're importing **Spring's** `@Transactional` — this is called out specifically because it's a genuinely common mistake to import the wrong one, especially in lab exercises.

## Recap

- Spring separates transaction demarcation (declared in your code via `@Transactional`) from transaction implementation (configured via a `PlatformTransactionManager` bean) — switching implementations is a configuration change, not a code change.
- Setting up declarative transaction management takes two steps: declare a `PlatformTransactionManager` bean, and mark transactional methods with `@Transactional`, backed by `@EnableTransactionManagement`.
- `@Transactional` methods run through a Spring proxy containing a `TransactionInterceptor`, which begins the transaction before delegating to your business logic, then commits or rolls back afterward.
- By default, an unchecked exception triggers a rollback, while a checked exception still commits — a default that can be overridden.
- The current transaction is bound to the thread via a thread-local, which is exactly how `JdbcTemplate` automatically reuses the right connection inside a transactional method.
- `@Transactional` can be applied at the class level (as a default for every method) and overridden per method — and you must import Spring's own `@Transactional`, not the JTA `jakarta.transaction`/`javax.transaction` version, to get access to its full set of properties.

## Check your understanding

1. What two steps are required to get declarative transaction management working in a Spring application, and which annotation activates the proxy machinery behind them?
2. By default, does a checked exception thrown from inside an `@Transactional` method commit or roll back the transaction — and how does that compare to an unchecked exception?
3. Why does `JdbcTemplate` automatically participate in an already-open transaction without any extra code in your repository methods?

The next lesson builds on this foundation by looking at how to configure transaction propagation — controlling what happens when a transactional method calls another transactional method.
