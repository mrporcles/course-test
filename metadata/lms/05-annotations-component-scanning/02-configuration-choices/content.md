## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Know exactly when `@Autowired` is optional versus required on a constructor
- Scope `@ComponentScan` correctly, and explain why scanning too broadly is a real performance problem
- Decide, with concrete criteria, when to reach for annotations versus Java-based configuration in the same project

## When you actually need \@Autowired on a constructor

the "Annotation-based Configuration" lesson introduced `@Autowired` for constructor injection, but it's easy to over-apply it out of habit. There are really only three cases:

- **A class with only a default (no-argument) constructor** — there's nothing to annotate; there's only ever one thing Spring could call.
- **A class with only one non-default constructor** — Spring will call that constructor because it's the only option available. `@Autowired` is optional here.
- **A class with more than one constructor** — this is the one case where the annotation is actually required. Without it, Spring falls back to the zero-argument constructor if one exists; if it doesn't, startup fails. Annotating the constructor you want with `@Autowired` is the only way to tell Spring which one to use.

You'll still see `@Autowired` used throughout examples even on single-constructor classes — that's purely for explicitness, to make the dependency injection visible at a glance. It's safe to omit in that case.

## Component scanning: why scope matters

Component scanning doesn't just scan your code — it scans everything on the classpath, including every JAR dependency your project pulls in. Get the scope wrong, and you pay for it in slow startup time, especially on larger applications.

Consider four increasingly better options:

- **Really bad:** `@ComponentScan({"org", "com"})` — this scans *every* `org` and `com` package on the entire classpath, including the Spring Framework's own packages and any third-party library you depend on. None of those JARs contain your application's components, so scanning them is pure waste.
- **Still bad:** `@ComponentScan("com")` — same problem, just narrowed slightly. You're still scanning far more than you need.
- **OK:** `@ComponentScan("com.bank.app")` — restricting the scan to your own base package is a reasonable baseline.
- **Optimized:** `@ComponentScan({"com.bank.app.repository", "com.bank.app.service", "com.bank.app.controller"})` — naming the exact packages that actually contain `@Component`-annotated classes (repository, service, controller layers, or whatever your project's layering looks like) is the tightest, fastest option.

The takeaway: component scanning happens at startup, and JAR dependencies get scanned too — the narrower and more deliberate your scan target, the faster and more predictable your application startup.

## Choosing between Java config and annotations

Both configuration styles from the "Annotation-based Configuration" lesson do the same job at the end of the day, so most real projects mix and match them. A common way to decide which to reach for in a given situation:

**Lean on annotations when:**
- Spring gives you no other choice — Spring MVC, for instance, requires annotations for many of its components.
- You're working with stereotype annotations (covered next, in the "Stereotype and Meta Annotations" lesson) for your own services, repositories, and controllers.

**Lean on Java configuration when:**
- You want or need to keep a bean's class fully decoupled from Spring — think legacy code, or code that needs to remain usable outside a Spring runtime entirely. You can't annotate a class you don't own, like a `DataSource` implementation that belongs to your infrastructure, not your application.
- Managing configuration from a single, centralized logical location is important to you — Java config lets you see everything in one class rather than scattered across your codebase.
- You need it to work for *any* class, not just the ones you wrote yourself — annotations only work on source you can modify; Java configuration works regardless.

Ultimately, how much of each style you use is your call — and it'll vary project to project. What matters far more than which style you pick is being **consistent** about it within a given codebase, so the rest of your team isn't left guessing why one service is configured one way and another is configured completely differently.

## Recap

- `@Autowired` is only strictly *required* when a class has more than one constructor and you need to tell Spring which one to use; it's optional (though sometimes used for clarity) in the single-constructor and default-constructor cases.
- Component scanning walks the entire classpath, JAR dependencies included — scope it to your own package structure, and ideally to the specific packages that actually hold your components, to avoid unnecessary startup cost.
- Prefer annotations for your own services, repositories, and controllers, especially where Spring requires them (like Spring MVC) or where stereotype annotations apply.
- Prefer Java configuration for beans you don't own, for centralizing configuration in one place, or for configuring any class regardless of whether it can be annotated.
- Consistency across a project matters more than which specific style you pick.

## Check your understanding

1. If a class has two constructors and neither is annotated with `@Autowired`, what will Spring do — and when would that actually fail?
2. Why is `@ComponentScan({"org", "com"})` a serious performance problem, even though it will technically still find your application's components?
3. Give an example of a bean you'd choose to configure with Java config rather than annotations, and explain why annotations wouldn't be an option there.

The next lesson moves into the bean lifecycle itself, starting with the `@PostConstruct` and `@PreDestroy` annotations.
