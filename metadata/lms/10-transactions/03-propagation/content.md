## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain what "propagation" means when one transactional method calls another
- Describe the default `REQUIRED` propagation and when Spring creates a new transaction versus joining an existing one
- Configure a method to always start its own independent transaction using `REQUIRES_NEW`
- Explain why changing propagation on an internally-called method has no effect, based on how Spring's proxies work

## Why propagation matters

the "Spring Transaction Management" lesson introduced declarative transaction management with `@Transactional`, using sensible defaults. This lesson looks at one of those defaults you can override: **propagation** — the rule that decides what happens to a transaction when a transactional method calls another transactional method.

Consider this example: `ClientServiceImpl.updateClient(...)` is transactional, and internally it calls `AccountServiceImpl.update(...)`, which is also transactional.

```java
public class ClientServiceImpl implements ClientService {
    @Autowired
    private AccountService accountService;

    @Transactional
    public void updateClient(Client c) {
        // ...
        this.accountService.update(c.getAccounts());
    }
}

public class AccountServiceImpl implements AccountService {
    @Transactional
    public void update(List<Account> accs) { /* ... */ }
}
```

When `updateClient` calls `update`, what should happen to the transaction? Should the two methods share a single transaction, or should each get its own, separate transaction? That question is exactly what propagation answers.

Spring defines seven propagation levels in total, covering every combination of "is there already a transaction?" and "what should I do about it?" This lesson focuses on the two most common ones: `REQUIRED` and `REQUIRES_NEW`. (The others — `SUPPORTS`, `MANDATORY`, `NOT_SUPPORTED`, and so on — are documented, but rarely needed day to day.)

Propagation is set through the `propagation` attribute on `@Transactional`, alongside the other attributes you already know:

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void update(List<Account> accs) { /* ... */ }
```

## `REQUIRED`: the default

`REQUIRED` is the propagation level you get automatically if you don't specify one. Its rule is simple: **run within a transaction, using an existing one if there is one, or creating a new one if there isn't.** Spring doesn't care whether a transaction already exists — it just guarantees that one exists by the time your code runs.

![REQUIRED: execute within a current transaction, create a new one if none exists](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/10-transactions/03-propagation/images/lesson40-required-diagram.png)

```java
@Transactional(propagation = Propagation.REQUIRED)
```

Going back to the `ClientServiceImpl` / `AccountServiceImpl` example: calling `updateClient` starts a new transaction (there wasn't one yet). When `updateClient` then calls `update`, `update` simply **joins** that same, already-running transaction — no second transaction is created. If you instead called `update` directly, with no transaction already active, it would start a new one itself, because `REQUIRED` always guarantees a transaction either way.

This is why `REQUIRED` is the sensible default: your service layer typically calls into several repositories in a row, and you want all of those calls to participate in one single transaction, not several independent ones.

## `REQUIRES_NEW`: always start fresh

Sometimes you want the opposite: a method that always runs in its *own* transaction, regardless of what's already happening around it. That's `REQUIRES_NEW`.

![REQUIRES_NEW: create a new transaction, suspending the current one if one exists](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/10-transactions/03-propagation/images/lesson40-requires-new-diagram.png)

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
```

If you call a `REQUIRES_NEW` method directly, with no transaction active, it simply starts a new one — same as `REQUIRED` would in that situation. The interesting case is when you call it from *inside* an existing transaction: the existing transaction is **suspended**, a brand-new, independent transaction is created and run to completion, and only then is the original transaction **resumed**.

Crucially, the two transactions are not nested — they are completely independent. That means transaction 2 can commit even if transaction 1 later rolls back, or vice versa. This matters in practice: if an inner `REQUIRES_NEW` method commits its work, that work stays committed even if the outer transaction subsequently fails and rolls back.

## Propagation rules are enforced by a proxy

Remember from the "Spring Transaction Management" lesson (and the AOP proxy discussion earlier in the course) that `@Transactional` behavior is added through an **around advice** applied by a proxy — Spring wraps your bean in a proxy object that intercepts calls and adds the transactional behavior before and after the real method runs.

This has an important consequence: **propagation only takes effect on calls that go through the proxy.** A call from outside the bean — through the injected interface — goes through the proxy. A call from *inside* the same class to one of its own methods does not; it's a plain Java method call on `this`, bypassing the proxy entirely.

```java
public class ClientServiceImpl implements ClientService {
    @Transactional(propagation = Propagation.REQUIRED)
    public void update1() {
        update2();   // internal call — does not go through the proxy
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void update2() {
        // ...
    }
}
```

Even though `update2()` is annotated with `REQUIRES_NEW`, calling it from `update1()` in the example above never creates a new transaction. Because the call to `update2()` doesn't go through the proxy, the transaction interceptor never runs for that call, so its `@Transactional` annotation is effectively ignored. Both methods end up participating in the same transaction: `update1()` starts it (`REQUIRED`, no existing transaction), and `update2()` just continues running inside it, as if it had no annotation at all.

This is a direct consequence of how Spring AOP proxies work: they can only intercept calls that arrive from outside the object, through the proxy. Self-invocation — one method on a class calling another method on the same class — never passes through that boundary.
