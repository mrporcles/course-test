## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain the difference between explicit, Java-based configuration and implicit, annotation-based configuration
- Use `@Component` and `@ComponentScan` to let Spring discover and register beans automatically
- Perform constructor, method, and field injection with `@Autowired`, and explain why constructor injection is the recommended default
- Resolve ambiguous autowiring situations with `@Qualifier` and by-name matching
- Use `@Value` and `@Lazy` to inject external configuration and defer bean creation

## From explicit to implicit configuration

Every configuration technique you've used so far has been **explicit**: a `@Configuration` class with `@Bean` methods that spell out, in one place, every component that belongs in the application context. That gives you flexibility, type safety, and a clean separation of concerns — your configuration is completely decoupled from your business logic.

Annotation-based configuration flips that around. Instead of describing your beans from the outside, you describe them from the inside — directly on the class itself.

![Before: explicit bean definition](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/05-annotations-component-scanning/01-configuration/images/lesson15-before-explicit-bean-definition.png)

In the "before" picture, a `@Configuration` class explicitly declares a `TransferService` bean and wires an `AccountRepository` into it via a `@Bean` method.

![After: implicit configuration](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/05-annotations-component-scanning/01-configuration/images/lesson15-after-implicit-configuration.png)

In the "after" picture, that same wiring moves onto the `TransferServiceImpl` class itself: it's annotated directly with `@Component`, so Spring knows to manage it as a bean. The configuration class shrinks down to essentially nothing — `AnnotationConfig` no longer needs any bean definitions at all.

The term "annotation-based configuration" can be a little misleading, since the Java-based configuration you've already seen also uses annotations (`@Configuration`, `@Bean`, and so on). What distinguishes this style is *where* the configuration lives: embedded directly in your business classes, rather than externalized into a dedicated configuration class.

## Component scanning

Annotating a class with `@Component` only works if Spring actually goes looking for it. That's the job of **component scanning**: on your configuration class, `@ComponentScan` tells Spring to scan a base package — and all of its sub-packages — for any class annotated with `@Component` (or a related stereotype annotation, covered in the "Stereotype and Meta Annotations" lesson). Every class it finds gets initialized and added to the application context automatically.

## Dependency injection with \@Autowired

With Java configuration, dependency injection happens through method parameters on `@Bean` methods. With annotations, the equivalent tool is `@Autowired`, which works at three levels: constructor, method, and field.

**Constructor injection.** If a class has more than one constructor, annotate the one you want Spring to use with `@Autowired`; Spring will inject whatever arguments that constructor declares. If there's only a single constructor, you can omit the annotation entirely — Spring uses it anyway.

**Method injection.** You can annotate any method (historically called "setter injection," though it works on any method, not just setters) with `@Autowired`, and its arguments get injected the same way.

**Field injection.** You can also autowire a field directly. This lesson discourages it: annotations are processed by the framework, so outside of a running Spring context — in a plain unit test, for example — that injection never happens. You'd be forced to reach for reflection or mocking just to supply the dependency. Constructor or method injection avoids that problem entirely.

![Usage of @Autowired: constructor, method, and field injection](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/05-annotations-component-scanning/01-configuration/images/lesson15-usage-of-autowired.png)

## Required or optional dependencies

`@Autowired` assumes the dependency must exist. If Spring can't find a matching bean, the application context fails to start with an exception. Sometimes that's exactly the behavior you want — but if you've supplied a sensible default and want startup to succeed either way, you have two options:

- Set `required = false` on the `@Autowired` annotation.
- Autowire directly into a Java 8 `Optional<T>` instead. If a matching bean exists, the `Optional` will contain it; otherwise it's empty, and you check for it with a method like `isPresent()`.

Both approaches say the same thing to Spring — "don't fail startup if this isn't available" — just with slightly different call-site ergonomics.

## Constructor vs. setter injection: which one to use?

In practice, you'll likely use both. It helps to know what each one actually gives you.

**Constructors** make dependencies mandatory — there's no way to construct the object without them — and they let you make those dependencies immutable, since nothing forces you to expose a setter. They're also concise: you pass everything at once.

**Setters** are the only practical way to wire up circular dependencies (even though circular dependencies are generally a code smell worth avoiding in the first place). Setter-injected dependencies are inherently mutable, since a setter is by definition a way for outside code to change them later. They can also help if a constructor is getting overloaded with too many parameters, and — unlike constructor logic — setters are inherited automatically from a parent class.

The recommendation: prefer constructor injection, since it makes required dependencies explicit and immutable. But don't fight the design — if you're extending a class built around setter injection, use setter injection. Above all, be consistent across your project team.

## Resolving ambiguity with \@Qualifier

Autowiring by type runs into trouble the moment two beans implement the same interface. Take a `TransferService` that depends on `AccountRepository`, where both a `JpaAccountRepository` and a `JdbcAccountRepository` are annotated `@Component` and present in the context. Spring can't tell which one you want — and at startup you'll get a `NoSuchBeanDefinitionException`, somewhat confusingly, since there isn't zero matching beans, there are two. The message will say Spring expected a single bean but found two.

The fix is to fall back to autowiring **by name**, using `@Qualifier`:

```java
@Component("transferService")
public class TransferServiceImpl implements TransferService {
    @Autowired
    public TransferServiceImpl(@Qualifier("jdbcAccountRepository") AccountRepository repo) {
        ...
    }
}

@Component("jdbcAccountRepository")
public class JdbcAccountRepository implements AccountRepository { ... }

@Component("jpaAccountRepository")
public class JpaAccountRepository implements AccountRepository { ... }
```

`@Qualifier` says: "give me an `AccountRepository`, but specifically the one named `jdbcAccountRepository`." Since you're now matching by name, it's a good idea to explicitly name each bean (it's not mandatory — every bean gets a name either way — but relying on the generated one is fragile here).

It's worth asking, though, why you need two implementations of the same interface in the application context at all. Often you don't — Spring profiles (the "Handling Multiple Configurations" lesson) let you filter the context down to a single implementation per environment, which sidesteps the ambiguity problem entirely and lets you keep autowiring by type.

When Spring resolves an `@Autowired` dependency, it follows three steps, in order:

1. Look for a unique bean of the required type.
2. If there are multiple matches, use `@Qualifier` if one is supplied.
3. If there's still no qualifier, try matching the constructor/method/field **argument name** against a bean name.

That last step matters even without an explicit `@Qualifier`: if you have multiple `Queue` beans and a parameter or field literally named `ack`, Spring will look for a bean named `ack` as a last resort before giving up.

## Component names

If you don't explicitly name a component, Spring auto-generates one: the class name with its first letter lowercased. Relying on generated names is discouraged — rename the class later, and you silently rename the bean, breaking anything that autowires by name.

The broader recommendation, again, is to avoid needing named disambiguation in the first place — usually it's rare to have two beans of the same type in an `ApplicationContext`, and profiles are usually the better way to solve that problem than leaning on qualifiers everywhere.

## Injecting configuration values with \@Value

Beyond wiring beans together, `@Autowired` combined with `@Value` lets you pull values out of the environment — properties, environment variables, and so on — instead of injecting a bean from the context. This works the same way at the constructor, method, or field level, though the field-level option is discouraged for the same reasons as field injection generally.

## Delayed initialization with \@Lazy

By default, every bean is created eagerly, right when the application context starts — deliberately, so misconfiguration surfaces immediately as a fail-fast startup error rather than a mysterious runtime failure later. Occasionally, though, a bean is expensive to initialize, or depends on something that isn't ready yet, and you'd rather defer its creation until the first time it's actually needed. `@Lazy` does exactly that.

![Delayed initialization with @Lazy](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/05-annotations-component-scanning/01-configuration/images/lesson15-delayed-initialization.png)

Use it sparingly — this is a commonly misused annotation, and most beans genuinely are not lazy. Reach for it only when you have a specific reason, such as a bean whose dependency (like a mail server connection) might not be available the instant the process starts.

## Annotations vs. Java configuration, side by side

Laid out next to each other, annotation-based and Java-based configuration offer essentially the same set of options:

![Annotation syntax vs. Java configuration](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/05-annotations-component-scanning/01-configuration/images/lesson15-annotations-syntax-vs-java-config.png)

- Marking a class a component (`@Component`) vs. writing a `@Bean` method
- `@Scope` works identically on both styles
- Profiles (`@Profile`) work identically on both styles
- `@Lazy` works identically on both styles
- Dependency injection is available in both styles, just expressed differently

At the end of the day, it's the same set of capabilities — the choice between them, covered next in the "Configuration Choices" lesson, comes down to which style fits your situation better.

## Recap

- Java-based configuration is explicit and externalized; annotation-based configuration is implicit and embedded directly in your business classes via `@Component`.
- `@ComponentScan` tells Spring which base package (and sub-packages) to search for annotated classes.
- `@Autowired` performs dependency injection at the constructor, method, or field level; constructor injection is preferred because it makes dependencies mandatory and immutable.
- Use `required = false` or an `Optional<T>` parameter to make a dependency optional instead of mandatory.
- Ambiguous autowiring by type is resolved with `@Qualifier`, or as a last resort, by matching the argument name against a bean name.
- `@Value` injects environment/property values instead of beans; `@Lazy` defers bean creation until first use, but should be used sparingly.

## Check your understanding

1. Why is field injection discouraged even though `@Autowired` supports it?
2. You have two beans implementing `AccountRepository` and get a `NoSuchBeanDefinitionException` mentioning two matching beans. What are two different ways to resolve this, and which one avoids the ambiguity altogether rather than just working around it?
3. What's the practical risk of relying on Spring's auto-generated component names instead of naming your beans explicitly?

Next up, the "Configuration Choices" lesson looks at how to actually choose between these two configuration styles — Java-based and annotation-based — in a real project.
