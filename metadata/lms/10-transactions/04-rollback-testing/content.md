## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain Spring's default rollback rule: which exceptions trigger a rollback and which don't
- Override that default using the `rollbackFor` and `noRollbackFor` attributes on `@Transactional`
- Make an integration test transactional so it automatically rolls back after each test method
- Use `@Commit` to override that automatic rollback for a specific test

## The default rollback rule

the "Configure Transaction Propagation" lesson covered overriding transaction propagation. Propagation isn't the only attribute you can override on `@Transactional` — this lesson covers the **rollback rules**, which decide whether a failure inside a transactional method actually rolls the transaction back.

By default, Spring only triggers a rollback if the method throws a **`RuntimeException`** (an unchecked exception). In this example, `rewardAccountFor` is transactional, and throwing a `RuntimeException` triggers a rollback:

```java
public class RewardNetworkImpl implements RewardNetwork {
    @Transactional
    public RewardConfirmation rewardAccountFor(Dining d) {
        // ...
        throw new RuntimeException();   // triggers a rollback
    }
}
```

In practice, this covers most of what you'll actually throw: if you're using Spring, exceptions you get back are typically runtime exceptions — for example, the `DataAccessException` hierarchy from the data access layer (recall the "Exception Handling" lesson). Other libraries follow the same convention; Hibernate, for instance, throws its own runtime exceptions too.

The problem case is a **checked exception** from a third-party library. Since checked exceptions aren't `RuntimeException`s, Spring's default rule leaves them alone — and by default, that means the transaction **commits**, even though an exception was thrown.

## Overriding the rollback rules

Spring gives you two attributes on `@Transactional` to change this default: **`rollbackFor`** and **`noRollbackFor`**. Use `rollbackFor` to force a rollback for exception types that wouldn't normally trigger one (like a checked exception), and `noRollbackFor` to do the opposite — suppress a rollback for a runtime exception type that would otherwise trigger one.

```java
public class RewardNetworkImpl implements RewardNetwork {
    @Transactional(rollbackFor = MyCheckedException.class,
                    noRollbackFor = {JmxException.class, MailException.class})
    public RewardConfirmation rewardAccountFor(Dining d) throws Exception {
        // ...
    }
}
```

In this example, `rewardAccountFor` is configured to roll back for a specific checked exception, `MyCheckedException`, even though it's not a `RuntimeException`. At the same time, it's configured to *not* roll back for two runtime exception hierarchies it would otherwise trigger a rollback for — `JmxException` and `MailException`. Both attributes accept multiple classes, so you can build up whatever combination of rules your method actually needs.

## Making tests transactional

The second half of this lesson is about bringing transactions into your test code — using the exact same `@Transactional` annotation you already use in production code, just with a different, and very useful, side effect.

Annotate a test method (or the whole test class) with `@Transactional`:

```java
@SpringJUnitConfig(RewardsConfig.class)
public class RewardNetworkTest {
    @Test
    @Transactional
    public void testRewardAccountFor() {
        // ...
    }
}
```

A transaction now starts automatically before the test method runs — but instead of committing at the end, like production code normally would, **the test's transaction is always rolled back**, regardless of whether the test passed or failed. That flips the usual behavior on its head, and it's deliberate: because every test starts from a clean transaction and rolls it back afterward, there's no leftover data in the database, and no manual cleanup step needed between test runs.

One detail worth remembering: the test framework only rolls back the **outermost** transaction — the one it created for the test itself. If your test (or the code it calls) starts an independent transaction of its own — for example, through `REQUIRES_NEW`, as covered in the "Configure Transaction Propagation" lesson — that independent transaction is not automatically rolled back by the test infrastructure. It commits on its own terms, exactly like it would outside a test. (The lab in the "Walkthrough - Transaction Management with Spring Lab" lesson walks through exactly this scenario.)

## Overriding the test's rollback with \@Commit

If you want a specific test method to keep its default, non-test behavior — committing instead of rolling back — annotate it with `@Commit`.

```java
@SpringJUnitConfig(RewardsConfig.class)
@Transactional
public class RewardNetworkTest {
    @Test
    @Commit
    public void testRewardAccountFor() {
        // Whatever happens here will be committed
    }
}
```

Here, `@Transactional` is applied at the class level, making every test method in the class transactional (and therefore rolled back by default). `@Commit` on `testRewardAccountFor` overrides just that one method, so its transaction is committed at the end instead of rolled back — useful for the occasional test where you actually want the data to persist.

That closes out the transaction management topics: declarative transaction management with `@Transactional` (the "Spring Transaction Management" lesson), overriding propagation (the "Configure Transaction Propagation" lesson), and now the transaction attributes and testing support covered here.
