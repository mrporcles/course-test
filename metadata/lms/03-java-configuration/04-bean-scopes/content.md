## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain what a bean's scope actually controls, and name the default scope
- Demonstrate the difference between singleton and prototype scope using `getBean`
- Explain why singleton beans need to be thought about carefully in multi-threaded applications
- List the web-specific scopes Spring provides, and know where to look if you need something more specialized
- Summarize why dependency injection, as covered across this module, matters

## What a scope actually controls

A bean definition — whatever you write inside a `@Bean` method (the "Quick Start with Java Configuration" lesson) — is really just a recipe for creating a component. The **scope** of a bean is what decides *how* that recipe gets used: does Spring run it once and reuse the result forever, or does it run the recipe again every single time the bean is requested? That's what this lesson explores.

## Singleton: the default scope

If you don't explicitly set a scope, your bean is treated as a **singleton**. Importantly, this doesn't mean you have to implement the Singleton design pattern in your own code — it just means Spring, at the container level, treats your component as a singleton: it's initialized once and then cached inside the application context.

You can make this explicit with the `@Scope` annotation:

```java
@Bean
public AccountService accountService() {
    return ...
}

@Bean
@Scope("singleton")
public AccountService accountService() {
    return ...
}
```

These two definitions are equivalent — the second is just spelling out, explicitly, the behavior you already get by default.

You can see this in action by asking the context for the same bean ID more than once:

```java
AccountService service1 = (AccountService) context.getBean("accountService");
AccountService service2 = (AccountService) context.getBean("accountService");
assert service1 == service2;  // True – same object
```

Comparing the two references shows they're the exact same instance. There is only ever one instance of a singleton-scoped bean living in the application context.

### Why singleton beans need extra care

Singleton beans deserve a second thought because they're typically accessed by multiple threads at the same time. Think of a typical Spring back-end web server: many requests are being processed in parallel, each handled by its own thread — but all of those threads are reaching into the *same* singleton services and repositories.

That means you need those beans to be thread-safe. Broadly, you have two options:

- **Make your components stateless** — this is the most common approach. If a bean holds no mutable state, there's nothing for concurrent threads to corrupt.
- **Synchronize any state you do maintain.** Concurrency in Java is hard, so if a bean does hold state, you need to make sure access to it is properly synchronized.

A third option, mentioned only briefly here, is to simply use a different scope — which is exactly what's covered next.

## Prototype scope

The **prototype** scope creates a brand-new instance every single time the bean is requested or injected:

```java
@Bean
@Scope("prototype")
public Action deviceAction() {
    return ...
}
```

```java
Action action1 = (Action) context.getBean("deviceAction");
Action action2 = (Action) context.getBean("deviceAction");
assert action1 != action2;  // True – different objects
```

Comparing the two references this time shows they're completely different instances — every call to `getBean` (or every injection point) triggers the recipe again, producing a fresh object.

## Other scopes available

Singleton and prototype are the two core scopes, but if you're working in a web application, several more become available:

| Scope | Behavior |
|---|---|
| `singleton` | A single instance is used |
| `prototype` | A new instance is created each time the bean is referenced |
| `session` | A new instance is created once per user session — web environment only |
| `request` | A new instance is created once per request — web environment only |

`session`-scoped beans are created when a new session starts and destroyed when that session ends. `request`-scoped beans are shorter-lived still — created fresh for, and destroyed at the end of, a single request.

Beyond those, Spring has other, more specialized scopes:

- **WebSocket scope** — lives for the duration of a WebSocket session; introduced in Spring 4.
- **Refresh scope** — belongs to Spring Cloud, and allows you to refresh a single component inside the application context.
- **Thread scope** — implemented in Spring but *not* registered by default; you'd have to explicitly register it yourself.
- **Custom scopes** — rare, but available. If you had, say, a multi-tenant application, you could define your own "tenant" scope by implementing the `Scope` interface and registering it under a custom name.

These more specialized scopes aren't covered in depth in this course, but it's worth knowing they exist.

## Why dependency injection matters (a quick recap)

Bean scopes are the last piece of a bigger picture built up over the last few lessons: dependency injection. Components don't go looking for their own dependencies — the container injects those dependencies for them. Because components typically depend on interfaces rather than concrete implementations, this decouples them from each other, and it also makes them far easier to test: a component with no dependency on the framework itself, and no hard dependency on a specific implementation of its collaborators, is easy to stub out in a unit test.

The application context, as covered across the "The Application Context" and "Handling Multiple Configurations" lessons, is the piece of the framework responsible for managing all of this — creating the beans, injecting the dependencies, and now, as this lesson has shown, deciding how many instances of each bean actually exist.

## Recap

- A bean's **scope** controls how many instances of it Spring creates, and when.
- **Singleton** is the default: one instance, created once, cached in the context, and shared by every caller.
- **Prototype** creates a brand-new instance every time the bean is requested.
- Singleton beans are typically accessed by multiple threads at once — make them stateless, synchronize their state, or choose a different scope.
- Web-specific scopes (`session`, `request`) create one instance per session or per request, respectively.
- More specialized scopes exist (WebSocket, Refresh, Thread, and fully custom scopes), though they're outside the scope of this course.

## Check your understanding

1. If you don't put any `@Scope` annotation on a `@Bean` method, what scope does it get, and what does that mean in terms of how many objects get created?
2. Why do singleton beans need special attention in a typical multi-threaded web application, and what are the two main ways to address that?
3. What would you expect `context.getBean("someProtoypeBean") == context.getBean("someProtoypeBean")` to evaluate to, and why?

The next module moves into a hands-on lab, putting everything from Java-based configuration — bean definitions, dependency injection, and application context creation — into practice on a real project.
