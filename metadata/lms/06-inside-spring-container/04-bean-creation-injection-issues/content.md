## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain how Spring recursively resolves bean dependencies, and how to force an explicit ordering with `@DependsOn`
- Compare how a bean's name and type are determined under Java config versus annotation-based configuration
- Diagnose a dependency-injection failure caused by an under-expressive `@Bean` return type
- Apply two different fixes for that problem, and explain Spring's best-practice guidance for choosing between them

## The piece we skipped: finding and creating dependencies

Back in the "Initialization Phase (Part 2)" lesson, the initialization-phase diagram had one box we didn't open up yet: finding and creating a bean's dependencies. Since Spring tries to create beans in the right order based on their dependencies, it first needs to know what those dependencies actually are.

This happens in two steps: evaluate the dependencies for every bean, then get each dependency that's needed — creating it first if it doesn't already exist. That second step is **recursive**: Spring keeps creating dependencies-of-dependencies until it reaches something it can actually inject.

## Forcing dependency order with `@DependsOn`

Normally, Spring figures out ordering on its own by walking the dependency graph — you don't need to intervene. But if you want to be explicit about ordering anyway, `@DependsOn` lets you do that directly.

```java
@Component
@DependsOn("accountService")
class TransferService {
    ...
}
```

```java
@Bean
@DependsOn("accountService")
public TransferService transferService() {
    return ...;
}
```

`@DependsOn` works identically for both Java config and annotation-based configuration, and can be placed at the class level or the bean-method level. In the example above, `TransferService` will always be created right after the bean named `accountService`, regardless of what Spring's own dependency analysis would have concluded.

## How bean name and type are determined

Java config and annotation-based configuration determine a bean's name and type differently, and the difference matters more than it might seem at first.

| | Name | Type |
|---|---|---|
| **1. Java config** | From `@Bean`'s `name`/`value` attribute, or from the method name | From the method's **return type** |
| **2. Annotation-based config** | From the annotation's `value` attribute, or derived from the class name | From the **annotated class itself** |

The key distinction: Java config's `@Bean` method typically returns an *interface*, while annotation-based config always gives you the *actual implementation class*, because the type comes straight from whatever class carries the annotation. That difference is exactly what causes the problem in the next section.

## When a bean's declared type isn't expressive enough

Consider a class that implements two interfaces:

```java
// TransferService does not extend BankService
class BankTransferServiceImpl
        implements TransferService, BankService {
    ...
}
```

```java
@Configuration
class Config {

    @Bean
    public BankingClient bankingService(BankService svc) {
        return new BankingClient(svc);
    }

    @Bean
    public TransferService transferService(AccountRepository repo) {
        return new BankTransferServiceImpl(repo);
    }
    ...
}
```

`bankTransferServiceImpl` implements both `TransferService` and `BankService` — but its `@Bean` method only declares a return type of `TransferService`. That's a **partial** picture: as far as the container's metadata is concerned, this method only produces a `TransferService`. The second bean method needs a `BankService` injected, but Spring has no record that a `BankService` will ever exist in the context — so that injection point fails, even though the actual object being created absolutely would satisfy it.

This matters because Spring gathers all of this dependency and type information *before* it starts creating anything, purely by inspecting method signatures. If the signature under-promises, Spring can't know better.

## Fixing it: two ways to be more expressive

**Solution 1 — return the implementation type.** Change the declared return type of the `@Bean` method to the concrete class instead of the narrower interface:

```java
// BankTransferServiceImpl is a BankService
class BankTransferServiceImpl
        implements TransferService, BankService {
    ...
}
```

```java
@Bean
public BankTransferServiceImpl transferService(AccountRepository repo) {
    return new BankTransferServiceImpl(repo);
}
```

Now the container knows a `BankService` will exist too, and the injection point that needs one resolves correctly.

**Solution 2 — introduce a composite interface.** Rather than exposing the concrete implementation type, define a new interface that combines both:

```java
// BankTransferServiceImpl is a BankService
interface BankTransferService
        extends TransferService, BankService {
}

class BankTransferServiceImpl
        implements BankTransferService { ... }
```

Have `BankTransferServiceImpl` implement this composite interface, and return the composite interface from the `@Bean` method. The container now has enough information to satisfy both injection points, while you're still returning an interface rather than a concrete class.

## Best practice: be "sufficiently expressive," but still inject interfaces

The guiding principle here is to be **"sufficiently expressive."**

- Return interfaces from your `@Bean` methods, *except* where a bean needs to satisfy multiple interfaces that are each needed for dependency injection elsewhere — in that specific case, be more explicit (Solution 1 or Solution 2 above).
- Writing to interfaces in general is still good practice.
- **Warning:** even if you do return implementation types, you should still *inject* using interfaces at your injection points, not the concrete class. Injecting concrete types is brittle — that dependency injection may fail later if the bean ends up being proxied (the "Use and Destroy Phases" lesson) or if a different implementation is substituted in.

This closes out the bean lifecycle module. Across the bean lifecycle lessons, you've seen the full lifecycle in depth — initialization, use, and destroy — plus the two families of extension points: `BeanFactoryPostProcessor`, which post-processes bean *definitions*, and `BeanPostProcessor`, which post-processes bean *instances*. And now you've seen the kinds of dependency and type-visibility issues that can trip you up when defining beans.

## Recap

- Spring resolves dependencies recursively before creating beans; `@DependsOn` lets you force an explicit creation order when you need one.
- Java config determines a bean's name and type from the `@Bean` method (name/method name, type/return type); annotation-based config determines both from the annotated class itself.
- Because Java config can return a narrower interface than the actual implementation provides, other beans that depend on a *different* interface implemented by that same class can fail to resolve.
- Fix it by either returning the more specific implementation type, or by introducing a composite interface that captures everything the bean actually provides.
- Aim to be "sufficiently expressive" in your return types — but keep injecting via interfaces regardless, since injecting concrete types is brittle.

## Check your understanding

1. Why does an annotation-based (`@Component`) bean never run into the "under-expressive return type" problem that a Java config `@Bean` method can?
2. A class implements three interfaces, but only one of them is ever used for dependency injection elsewhere in your application. Do you need a composite interface here? Why or why not?
3. Even after applying Solution 1 and returning the concrete implementation type from your `@Bean` method, what should you still do at the injection points that consume that bean, and why?

With the bean lifecycle now fully covered, the next module turns to a different kind of problem entirely: how Aspect-Oriented Programming lets you modularize behavior — like security, transactions, and logging — that would otherwise be duplicated across your entire codebase.
