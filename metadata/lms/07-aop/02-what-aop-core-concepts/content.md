## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Define the five core AOP vocabulary terms: join point, pointcut, advice, aspect, and weaving
- Explain what an AOP proxy is and why Spring wraps your bean in one
- Build a first working aspect using `@Aspect`, `@Component`, `@Before`, and a pointcut expression
- Wire AspectJ-style configuration into a Spring application with `@EnableAspectJAutoProxy`
- Use the `JoinPoint` parameter to access context — method name, arguments, target — from inside an advice method

## Learning the vocabulary first

Before writing any AOP code, it helps to have the vocabulary down — much like learning terms like polymorphism, inheritance, class, and instance before diving into object-oriented programming. This lesson introduces the concepts you'll be using throughout the rest of the module.

## Join point, pointcut, advice, aspect, and weaving

- **Join point** — a point in the execution of a program, such as a method call or an exception being thrown. Spring AOP only supports method calls as join points, so for everything in this course, "join point" effectively means "a method call."
- **Pointcut** — an expression, written in the AspectJ expression language, that selects one or more join points. You'll build these expressions in the next lesson.
- **Advice** — the code you actually want to execute at a matched join point.
- **Aspect** — the encapsulation of *what* to run and *where* to run it. An aspect is what ties an advice together with a pointcut.
- **Weaving** — the technique used to apply aspects into your application — the mechanism that actually adds this behavior at runtime.

## What is a proxy?

A **proxy**, generally, is something that stands in place of someone or something else — a person who votes on your behalf at a shareholders' meeting is a human proxy; a web proxy that routes your traffic through a corporate firewall on its way to the internet is another kind. An **AOP proxy** is the same idea applied to your classes: it's a class that behaves like some other class, standing in its place, and it's how Spring *enhances* your original class with things like transactions, security, and caching — whatever behavior you need.

## A quick-start requirement: log every property change

With the vocabulary in place, here's a simple requirement to build against: log a message every time a property is about to change — in other words, every time a setter method is called.

## The starting point: a plain `SimpleCache` class

```java
public interface Cache {
    public void setCacheSize(int size);
    public void setTimeout(int ms);
}

public class SimpleCache implements Cache {
    private int cacheSize, ms;
    private String name;

    public SimpleCache(String beanName) { name = beanName; }

    public void setCacheSize(int size) { cacheSize = size; }
    public void setTimeout(int ms) { ms = ms; }
    ...

    public String toString() { return name; }   // For convenience later
}
```

`SimpleCache` implements a `Cache` interface with `setCacheSize` and `setTimeout`. Nothing here changes to satisfy the logging requirement — that's the whole point of AOP: the business logic stays untouched.

## Writing the aspect

We modularize the cross-cutting concern (logging on property change) into its own aspect:

```java
@Aspect
@Component
public class PropertyChangeTracker {
    private Logger logger = Logger.getLogger(getClass());

    @Before("execution(void set*(*))")
    public void trackChange() {
        logger.info("Property about to change...");
    }
}
```

A few things worth calling out:

- `@Aspect` is *not* a Spring-specific annotation — it comes from AspectJ. It marks this class as encapsulating an aspect (the "what" and the "where").
- `@Component` *is* needed separately, because the aspect class still has to be a Spring-managed bean like anything else.
- The `trackChange()` method is annotated `@Before` — this defines the **advice**. Its body is the code that runs at the matched join point. (Don't confuse this `@Before` with JUnit's `@Before` — this one is an AspectJ annotation.)
- The string inside `@Before(...)` is the **pointcut** expression — the "where." `execution(void set*(*))` matches any method starting with `set`, taking exactly one argument, and returning `void`. (The next lesson covers this expression syntax in depth.)

## Wiring it into the application

Two more pieces are needed: turning on AspectJ-style weaving, and defining the actual beans.

```java
@Configuration
@EnableAspectJAutoProxy
@ComponentScan(basePackages = "com.example.aspects")
public class AspectConfig {
}
```

`@EnableAspectJAutoProxy` enables the weaving process — but despite the name, this does *not* mean Spring switches to the AspectJ bytecode weaver. Spring AOP uses the *AspectJ configuration style and expression language*, while still weaving with proxies, not bytecode modification. The `@ComponentScan` here scans specifically for the package containing your aspects.

```java
@Configuration
@Import(AspectConfig.class)
public class MainConfig {

    @Bean
    public Cache cacheA() { return new SimpleCache("cacheA"); }

    @Bean
    public Cache cacheB() { return new SimpleCache("cacheB"); }

    @Bean
    public Cache cacheC() { return new SimpleCache("cacheC"); }
}
```

`MainConfig` defines three beans of the same `SimpleCache` type, distinguished only by name, and imports `AspectConfig` so that the aspect and its proxy-creation machinery are active in the same application context.

## Running it and seeing the advice fire

```java
ApplicationContext context = SpringApplication.run(MainConfig.class);

@Autowired
@Qualifier("cacheA")
private Cache cache;
...
cache.setCacheSize(2500);
```

Calling `setCacheSize(2500)` on the `cacheA` bean should print something like `INFO: Property about to change...` to the console — the advice ran *before* the setter's actual logic. That's only possible because `cache` here is a proxy, not your raw `SimpleCache` object.

Here's the full picture of what happens:

![How Aspects are Applied](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/07-aop/02-what-aop-core-concepts/images/lesson25-how-aspects-are-applied.png)

1. Spring creates a proxy during initialization, weaving together the aspect and the target.
2. The proxy implements the same interface(s) as the target — here, `Cache` — so it behaves like a `Cache` from the caller's point of view. (Since `SimpleCache` implements an interface, this is a JDK proxy — see the "Use and Destroy Phases" lesson.)
3. Every call — `setCacheSize(2500)` in this example — is routed through the proxy's method interceptor first, not straight to your target.
4. The interceptor checks whether the pointcut matches, and if it does, executes the matching advice — here, `PropertyChangeTracker`.
5. Only after the advice runs does the call delegate to the actual target, `SimpleCache`, to execute the real business logic.

Because this was a `@Before` advice, it only runs *before* delegation to the target; there's nothing to run afterward, so control returns straight to the caller once the target method completes.

## Only interface methods get proxied

Since setters get proxied through the interface, only the methods actually declared on that interface are covered.

```java
public class DatabaseCache implements Cache {
    private int cacheSize, ms;
    private DataSource dataSource;
    private String name;

    public SimpleCache(String beanName) { name = beanName; }

    public void setCacheSize(int size) { cacheSize = size; }
    public void setTimeout(int ms) { ms = ms; }
    public void setDataSource(DataSource ds) { dataSource = ds; }
    ...
}
```

`setCacheSize` and `setTimeout` are declared on `Cache`, so both are proxied and both trigger the advice. `setDataSource` is *not* part of the `Cache` interface — it only exists on the implementation — so with a JDK proxy, there's no way to even call `setDataSource` on a `Cache` retrieved from the application context, let alone have it trigger the advice.

## Getting context inside an advice: the `JoinPoint` parameter

Sometimes an advice method needs more information: which arguments were passed, which method was actually called, or a reference to the target or the proxy itself. You get all of that by adding a `JoinPoint` parameter to your advice method — Spring injects it automatically.

```java
@Aspect @Component
public class PropertyChangeTracker {
    private Logger logger = Logger.getLogger(getClass());

    @Before("execution(void set*(*))")
    public void trackChange(JoinPoint point) {
        String methodName = point.getSignature().getName();
        Object newValue = point.getArgs()[0];
        logger.info(methodName + " about to change to " +
                    newValue + " on " +
                    point.getTarget());
    }
}
```

`point.getSignature().getName()` gives you the method name that was called; `point.getArgs()` returns the arguments as an `Object[]`; and `point.getTarget()` (or `point.getProxy()`) gives you a reference back to the target or the proxy, respectively. In this example, `point.getTarget()` is concatenated into the log message, so the target's `toString()` is used; `SimpleCache.toString()` returns the bean name. Remember: you're executing *inside the aspect* here — not inside the proxy, and not inside the target — so these accessors are how you reach back out to either one.

## Recap

- The five core AOP terms: **join point** (a method call), **pointcut** (an expression selecting join points), **advice** (the code to run), **aspect** (advice + pointcut, the "what" and "where"), and **weaving** (applying aspects to your code).
- A proxy stands in for your original object; an AOP proxy specifically adds behavior (like logging, security, or transactions) around your bean, transparently.
- A minimal aspect needs `@Aspect` (AspectJ) plus `@Component` (Spring), an advice method annotated with something like `@Before`, and a pointcut expression string.
- `@EnableAspectJAutoProxy` turns on Spring AOP's proxy-based weaving using AspectJ's configuration style — it does not switch to AspectJ's own bytecode weaver.
- Only methods declared on the proxied interface are actually enhanced; implementation-only methods are invisible to a JDK proxy.
- Add a `JoinPoint` parameter to an advice method to access the intercepted method's name, arguments, target, or proxy.

## Check your understanding

1. What's the difference between a pointcut and an advice, and how does an aspect relate the two?
2. Why does `@EnableAspectJAutoProxy` not mean Spring is using AspectJ's bytecode weaver?
3. If `DatabaseCache` implements `Cache` and also has an extra `setDataSource` method, why doesn't `setDataSource` trigger the `PropertyChangeTracker` advice — and would that change if Spring used a CGLIB proxy instead of a JDK proxy?

You've now seen a pointcut expression in passing — `execution(void set*(*))` — without a full explanation of the syntax; the next lesson breaks down exactly how to read and write these expressions yourself.
