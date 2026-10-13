## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain what a stereotype annotation actually is, and why `@Service` behaves like `@Component`
- Name the predefined Spring stereotype annotations and the layer each one is conventionally used for
- Explain what a meta-annotation is, and define your own custom annotation that combines several Spring behaviors
- Configure a custom annotation correctly with `@Retention` and `@Target` so Spring can actually recognize it

## What a stereotype annotation is

Component scanning, as covered in the "Annotation-based Configuration" lesson, doesn't only look for `@Component`. It also scans for any annotation that is *itself* annotated with `@Component` — these are called **stereotype annotations**.

![Stereotype Annotations](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/05-annotations-component-scanning/04-stereotypes/images/lesson18-stereotype-annotations.png)

`@Service` is one of them. Looking at its own source code, `@Service` is annotated with `@Component`:

```java
@Target({ElementType.TYPE})
// ...
@Component
public @interface Service { ... }
```

Because of that, anything annotated `@Service` behaves exactly like it was annotated `@Component` — it gets picked up by `@ComponentScan` and added to the application context, just with a name that documents its role more precisely:

```java
@Service("transferService")
public class TransferServiceImpl implements TransferService { ... }
```

## The predefined stereotype annotations

Spring's core framework ships with a stereotype annotation for each conventional application layer, all ultimately rooted in `@Component`:

![Predefined Stereotype Annotations](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/05-annotations-component-scanning/04-stereotypes/images/lesson18-predefined-stereotype-annotations.png)

- **`@Service`** — service classes
- **`@Repository`** — data access classes
- **`@Controller`** and **`@RestController`** — web classes (Spring MVC)
- **`@Configuration`** — Java configuration classes

That last one is worth calling out: `@Configuration` is itself a stereotype annotation, which means your configuration classes are component-scanned too — you don't need `@Import` to pull them in, as long as they sit inside a scanned package.

Other Spring projects define their own stereotype annotations beyond this core set — Spring Web Services and Spring Integration, for instance, each add their own.

## Meta-annotations: building your own

What makes stereotype annotations especially useful is that they're **meta-annotations** — annotations that can themselves be used to annotate *other* annotations. That means you can define your own custom annotation that bundles together several Spring behaviors at once.

Say you want every service bean in your application to be both component-scanned *and* transactional (transaction management is covered later in this course). Rather than stacking `@Service` and `@Transactional` on every single class, you can define one custom annotation that carries both:

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@Service
@Transactional(timeout = 60)
public @interface MyTransactionalService {
    String value() default "";
}
```

Two attributes on the custom annotation matter here, and both are easy to get wrong:

- **`@Retention(RetentionPolicy.RUNTIME)`** — annotations are compiled out by default; Spring needs to inspect this one *after* compilation, at runtime, so retention must explicitly be set to `RUNTIME`.
- **`@Target(ElementType.TYPE)`** — this restricts where the annotation is legal to use. `TYPE` means class or interface level, which is exactly where you'd want to put a service-level annotation like this one.

With that in place, you can use your own annotation exactly like any built-in stereotype:

```java
@MyTransactionalService
public class TransferServiceImpl implements TransferService { ... }
```

Component scanning recognizes `@MyTransactionalService` the same way it recognizes `@Service` — because underneath, it's `@Service` (plus `@Transactional`) all along.

The next lesson puts all of this module's annotation-based configuration to work in a hands-on lab, before the course turns to the bean lifecycle itself in the "Initialization Phase (Part 1)" lesson.
