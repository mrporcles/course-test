## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain what happens when you retrieve a bean from the application context, and when Spring hands you a proxy instead of your original object
- Compare JDK dynamic proxies and CGLIB proxies, and know which one Spring Boot always chooses
- Trace a transactional method call through the proxy, the interceptor, and the transaction manager
- Describe what happens during the destroy phase, and its limitations around prototype beans and ungraceful shutdown

## From initialization to use

Once your components are fully configured and initialized (the "Initialization Phase (Part 2)" lesson), it's time to actually use them. Calling `SpringApplication.run(...)` hands you back the application context, with every component initialized and wired. From there, you can retrieve beans out of it with `getBean`:

```java
TransferService transferService = context.getBean("transferService", TransferService.class);
transferService.transfer(...);
```

## Case I: your bean is just your bean

If you retrieve a bean and it's exactly your own component, nothing special happens — calling a method just runs your business logic directly.

## Case II: your bean is a proxy

But sometimes what you retrieve from the context isn't your object at all — it's a **proxy** standing in for it.

![Case II: Your Bean is a Proxy](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/06-inside-spring-container/03-use-destroy-phases/images/lesson22-bean-is-a-proxy.png)

Spring reaches for a proxy whenever it needs to add extra behavior around your component transparently — transactions, security, and exception handling are the classic examples. This proxy creation happens during the initialization phase you already saw in the "Initialization Phase (Part 2)" lesson: it's done by one of the `BeanPostProcessor`s. Recall that a `BeanPostProcessor` receives the original bean and can return something else entirely — in this case, the post-processor inspects your bean, decides it needs a proxy, creates one, and hands *that* back to the application context instead. From then on, everything that looks up that bean gets the proxy.

## Walking through a transactional call

Here's what that looks like end to end for a transactional method:

![Proxy Power Example: Transactions](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/06-inside-spring-container/03-use-destroy-phases/images/lesson22-proxy-power-example-transactions.png)

1. The caller calls `transfer("$50", "1", "2")` — but they're calling the proxy, not `TransferServiceImpl` directly.
2. The proxy routes the call through a `SpringTransactionInterceptor`.
3. The interceptor delegates to a bean called the `TransactionManager` to **begin** the transaction.
4. The interceptor then delegates to the actual target — your `TransferServiceImpl` — which runs your business logic inside that transaction.
5. When the business logic finishes, control returns to the interceptor, which delegates to the `TransactionManager` again, this time to **commit** (or roll back) the transaction.
6. Control returns to the original caller.

Transactional behavior is added *around* the target — your bean itself has no idea any of this is happening.

## JDK proxies vs. CGLIB proxies

Spring supports two different mechanisms for building these proxies, and which one it uses depends entirely on how your class is designed.

![Kinds of Proxies](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/06-inside-spring-container/03-use-destroy-phases/images/lesson22-kinds-of-proxies.png)

- **JDK proxies** (also called *dynamic proxies*) are built into the JDK itself, but they *require* an interface — the proxy is generated to implement the same interface(s) as your class. If your class implements an interface, Spring will use a JDK proxy.
- **CGLIB proxies** are not built into the JDK; the library ships inside Spring's jars instead. CGLIB proxies work by extending your class, so no interface is required — which makes them the fallback when your class doesn't implement one. They cannot be applied to `final` classes or methods, since extension isn't possible there.

![JDK vs CGLIB Proxies](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/06-inside-spring-container/03-use-destroy-phases/images/lesson22-jdk-vs-cglib-proxies.png)

Notice the difference in relationship: a JDK proxy *implements* the same interface as your target (`TransferService`), while a CGLIB proxy *extends* your concrete class (`TransferServiceImpl`) directly. Either way, the proxy wraps "extra logic" around a reference to your original object, called the **target**.

Spring Boot specifically always chooses CGLIB, regardless of whether your class implements an interface — this technique of choosing between the two only really applies when you're working with plain vanilla Spring.

## A consequence of proxying: only interface methods are enhanced

This distinction has a practical consequence for JDK proxies in particular: since the proxy only implements the interface, only the methods declared on that interface get proxied. If your implementation class has an extra method that isn't part of the interface, you won't be able to call it through a bean retrieved from the application context — the proxy simply doesn't expose it.

## The destroy phase

Eventually, the application shuts down and beans need to be cleaned up. This is the third and final phase of the bean lifecycle, after initialization and use.

The destruction phase happens when the context is closed — either explicitly, by calling `close()` on a `ConfigurableApplicationContext`, or via a JVM shutdown hook.

When that happens:

1. Every registered `@PreDestroy` method is invoked (recall `@PreDestroy` from the "Adding Startup and Shutdown Behaviors" lesson — this is exactly when it runs).
2. Beans are released so the garbage collector can reclaim them.

A couple of important limits apply here. This clean-up process happens for non-prototype-scoped beans — singleton, request, session, WebSocket, and so on — but **not** for prototype-scoped beans, because the container has no way of knowing when a prototype bean goes out of scope or is no longer needed; it isn't tracking that bean's lifetime the way it does for other scopes. And critically, this only happens if the application shuts down *gracefully*. If the process is killed outright, there's no opportunity for the destruction phase to run at all.

Now that you've seen the full lifecycle — initialization, use, and destruction — the next lesson circles back to fill in a detail we skipped: exactly how Spring figures out the order to create your beans, and what can go wrong along the way.
