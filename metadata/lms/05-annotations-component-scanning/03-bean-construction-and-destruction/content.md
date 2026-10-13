## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain exactly where `@PostConstruct` and `@PreDestroy` fit in a bean's lifecycle relative to dependency injection
- Recognize that these are standard Java annotations, not Spring-specific ones
- Use the `initMethod`/`destroyMethod` attributes of `@Bean` as the equivalent technique for beans you can't annotate
- Explain why `@PreDestroy` isn't called for prototype-scoped beans, and how the context actually gets closed in practice

## What these annotations are for

So far you've seen annotations used for configuration (the "Annotation-based Configuration" lesson) and dependency injection (`@Autowired`). This lesson covers a different category: **lifecycle annotations** that run your own logic at specific points in a bean's life — right after it's fully constructed, and right before it's destroyed.

Both annotate methods that take **no arguments** and return **void** — that's the contract. It doesn't matter how the bean itself was created: whether it came back from an `@Bean` method or was found and created by the component scanner, Spring invokes these methods automatically during the bean-creation process.

Worth noting: these are not Spring-specific annotations. They're defined by **JSR-250**, and have been part of Java since Java 6. That's why you'll see them used in other frameworks too — Spring simply honors the standard rather than reinventing it.

> **Package name note:** starting with Spring Framework 6 / Spring Boot 3 (the `jakarta.*` namespace migration), and continuing through the current Spring Framework 7 / Spring Boot 4 generation (now on Jakarta EE 11), these annotations live in `jakarta.annotation`. Older Spring versions (Spring Framework 5.x and earlier, matching this course) used `javax.annotation` instead — the annotations and their behavior are identical, only the package name changed.

## \@PostConstruct: running logic after injection

`@PostConstruct` runs during the initialization phase, specifically **right after all dependency injection has completed** for that bean.

![@PostConstruct: called after setter injections are performed](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/05-annotations-component-scanning/03-bean-construction-and-destruction/images/lesson17-postconstruct-order.png)

Consider a `JdbcAccountRepository` that needs to populate an internal cache using a `DataSource` — but that `DataSource` is supplied via setter injection, not the constructor:

```java
public class JdbcAccountRepository {
    private DataSource dataSource;

    @Autowired
    public void setDataSource(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @PostConstruct
    public void populateCache() {
        Connection conn = dataSource.getConnection();
        // ...
    }
}
```

If you tried to run this cache-population logic directly in the constructor, it would be too early — the constructor runs before setter injection happens, so `dataSource` would still be `null`, and you'd get a `NullPointerException`. `@PostConstruct` exists precisely to solve that ordering problem: the full sequence Spring guarantees is **constructor injection, then setter injection, then any `@PostConstruct` methods**. By the time `populateCache()` runs, every dependency — regardless of which injection style supplied it — is already in place.

## \@PreDestroy: cleaning up before shutdown

`@PreDestroy` is the mirror image: it runs during the destruction phase, when the application context is closed.

```java
ConfigurableApplicationContext context = SpringApplication.run(...);
// ...
// Trigger call of all @PreDestroy annotated methods
context.close();
```

It's useful for releasing resources and general cleanup. Two details are worth keeping in mind:

- `@PreDestroy` methods only run if the application shuts down **normally**. If the process is killed outright (`kill -9`, as opposed to a graceful termination signal), there's no opportunity for the JVM — or Spring — to run any cleanup code at all.
- `@PreDestroy` is **not called for prototype-scoped beans**. Recall from earlier lessons that Spring hands off a prototype bean to the caller and stops tracking it — with no way to know when (or if) that instance is discarded, Spring has no moment at which it could reliably invoke a destroy callback.

## When you can't annotate the class

`@PostConstruct` and `@PreDestroy` only work if you can add annotations to the class itself. That's not always possible — a bean might come from a third-party library, or be a compiled class you don't have source access to. For those cases, `@Bean` exposes the same behavior through plain attributes instead:

```java
@Bean(initMethod = "populateCache", destroyMethod = "flushCache")
public AccountRepository accountRepository() {
    // ...
}
```

This gives you the same two lifecycle hooks — just declared where you configure the bean instead of on the bean's own class. The common convention: use `@PostConstruct`/`@PreDestroy` for your own classes, and the `initMethod`/`destroyMethod` attributes of `@Bean` for anything you don't own. (One extra option worth knowing: the "init" logic can also just be called directly, inline, in your own `@Bean` method body, in which case you don't need `initMethod` at all.)

## How the context actually gets closed

`@PreDestroy` callbacks only fire once `ConfigurableApplicationContext.close()` runs — either because you call it explicitly, or because Spring arranges for it to happen automatically.

![Using a JVM shutdown hook](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/05-annotations-component-scanning/03-bean-construction-and-destruction/images/lesson17-jvm-shutdown-hook.png)

If you start your application with `SpringApplication.run(...)`, Spring registers a **JVM shutdown hook** for you automatically:

```java
ConfigurableApplicationContext context = SpringApplication.run(...);
// Registered the shutdown hook for you
```

When the JVM shuts down — via `System.exit()`, `Runtime.exit()`, or a graceful process termination — that hook fires, tells the `ConfigurableApplicationContext` to close, and every `@PreDestroy`-annotated method runs as part of that shutdown. This only applies to a *graceful* shutdown; forcibly killing the process bypasses the hook entirely, and no cleanup code runs.

## Recap

- `@PostConstruct` and `@PreDestroy` are standard JSR-250 annotations (`jakarta.annotation` on Spring Framework 6+/Boot 3+; `javax.annotation` on earlier versions), not Spring-specific — Spring just knows how to honor them.
- The guaranteed order is constructor injection, then setter injection, then `@PostConstruct` methods — so by the time your post-construct logic runs, every dependency is already available.
- `@PreDestroy` runs when the context closes normally, but never for prototype-scoped beans, and never if the process is killed rather than terminated gracefully.
- For beans you don't own or can't annotate, use `@Bean(initMethod = "...", destroyMethod = "...")` as the equivalent mechanism.
- `SpringApplication.run(...)` registers a JVM shutdown hook automatically, so a graceful shutdown closes the context — and runs your `@PreDestroy` methods — without any extra code on your part.

## Check your understanding

1. Why would putting cache-population logic directly in a constructor be unsafe for a bean that uses setter injection, and how does `@PostConstruct` solve that?
2. Why doesn't Spring call `@PreDestroy` methods on prototype-scoped beans?
3. You're wiring up a `DataSource` bean from a third-party library that you can't modify. How would you hook into its initialization and cleanup lifecycle without `@PostConstruct`/`@PreDestroy`?

The next lesson turns to stereotype and meta-annotations — how annotations like `@Service` and `@Repository` build on top of everything you've seen so far.
