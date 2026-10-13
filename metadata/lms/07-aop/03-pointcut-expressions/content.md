## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Explain why Spring AOP pointcut expressions center on the `execution` designator, and how Spring AOP relates to the broader AspectJ expression language
- Read and write the `[Modifiers] ReturnType [ClassType] MethodName(Arguments) [throws ExceptionType]` method pattern, including the `*` and `..` wildcards
- Combine pointcuts into composite expressions using `&&`, `||`, and `!`
- Write expressions that match by concrete class, by interface, and by annotation
- Distinguish between the three ways to wildcard a package, and know which is broadest

## From advice to expressions

the "Core AOP Concepts and Quick Start" lesson showed how to implement an aspect, define an advice, and attach a pointcut — but glossed over exactly how those pointcut expressions are actually built. This lesson fills that gap using the **AspectJ expression language**.

## Spring AOP is a subset of AspectJ

Spring AOP and AspectJ share both their configuration style and their expression language — that's why `@Aspect` and the annotations you saw last lesson come from AspectJ rather than Spring itself. The full expression language is documented at `eclipse.org/aspectj/docs`, but it's worth knowing up front: **Spring AOP is a subset of AspectJ.** Not everything documented there is supported in Spring AOP. In practice, though, Spring AOP is more than enough for roughly 80% of real-world cases, and it integrates with the container without any extra configuration — which is exactly why this course sticks to it.

## The `execution` designator and method pattern

A pointcut expression is built around **designators**. AspectJ supports several, but Spring AOP focuses on just one: `execution`. That follows directly from something you already know — a Spring AOP join point is always a method invocation — so almost every expression you'll write starts with `execution(...)`.

Inside the parentheses is a **method pattern**:

```
[Modifiers] ReturnType [ClassType]
    MethodName (Arguments) [throws ExceptionType]
```

Two parts of this pattern are mandatory: the **return type** and the **method name with its arguments**. Everything else — modifiers, the class type, a thrown-exception clause — is optional and can be omitted.

You can also combine expressions with `&&` (and), `||` (or), and `!` (not) to build more complex, composite pointcuts by chaining simpler ones together — for example, `execution(pattern1) || execution(pattern2)`.

## Wildcards: `*` and `..`

Expressions use exactly two wildcards:

- **`*`** — matches exactly once: a single return type, package segment, class, method name, or argument.
- **`..`** — matches zero or more: either arguments, or package segments.

## Reading a full example

![Example Expression](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/07-aop/03-pointcut-expressions/images/lesson26-example-expression.png)

```
execution(* rewards.restaurant.*Service.find*(..))
```

The easiest way to read one of these is right to left:

- `find*(..)` — any **finder** method (starts with `find`), with zero or more arguments.
- `*Service` — inside any **class** whose name ends with `Service`.
- `rewards.restaurant` — in the **package** `rewards.restaurant`.
- the leading `*` — returning **any type**.

So altogether: any finder method, with any number of arguments, inside any class ending in `Service`, in the `rewards.restaurant` package, returning anything.

## Matching by argument type

```
execution(void send*(rewards.Dining))
```

Any method starting with `send`, taking a single argument of type `rewards.Dining`, returning `void`. Notice the argument type is given as a **fully qualified name** — `rewards.Dining`, not just `Dining`. That's because a pointcut expression is, at the end of the day, just a string; there's no type safety here, so anything that isn't a primitive or `String` needs its full package path.

```
execution(* send(*))
```

A method explicitly named `send`, taking exactly one argument of any type (`*` in the argument position means one and only one), returning anything.

```
execution(* send(int, ..))
```

A method explicitly named `send`, whose *first* argument must be an `int`, followed by zero or more additional arguments of any type, returning anything.

## Matching a concrete class — and its subclasses

```
execution(void example.MessageServiceImpl.*(..))
```

Reading right to left again: any method (`*`), with any arguments (`..`), on the class `MessageServiceImpl` in the package `example`, returning `void`. As with argument types, the class needs its fully qualified name — if you omit the package, the expression is interpreted as the root package, which is essentially never what you want; you either give just the method, or the fully qualified type, but never a bare class name without its package.

One subtlety worth remembering: this also matches any **subclass** of `MessageServiceImpl`. That's not obvious just from reading the expression, but as long as the type matches, subclasses match too.

## Matching an interface instead

```
execution(void example.MessageService.send(*))
```

You can target an interface instead of a concrete class for more flexibility — here, `example.MessageService` instead of the implementation. Anything that implements this interface will match the expression, not just one specific class.

## Matching by annotation

Sometimes there's no naming convention to match against — an annotation is often a better fit in that case.

```
execution(@jakarta.annotation.security.RolesAllowed void send*(..))
```

```java
public interface Mailer {
    @RolesAllowed("USER")
    public void sendMessage(String text);
}
```

This matches any void method starting with `send` that's annotated with `@RolesAllowed` — again using the fully qualified annotation name, since there's no type safety in these strings. (On Spring Framework 5.x and earlier, this annotation's package is `javax.annotation.security` instead of `jakarta.annotation.security` — the pointcut expression would need to match whichever package is actually on your classpath.) This is a particularly nice technique if you define your own custom annotations: you can write an advice that says, in effect, "run this for anything annotated with my annotation," regardless of naming or location.

## Working with packages

The last set of examples shows three closely related ways of wildcarding a package, each one broader than the last.

```
execution(* rewards.*.restaurant.*.*(..))
```
Any method, any arguments, in any class, inside a package where there is **exactly one** directory between `rewards` and `restaurant` — the single `*` only matches one path segment, so something like `rewards.internal.restaurant` qualifies, but `rewards.restaurant` itself or `rewards.a.b.restaurant` would not.

```
execution(* rewards..restaurant.*.*(..))
```
Same idea, but the `*` between `rewards` and `restaurant` is replaced with `..` — meaning **zero or more** sub-packages in between. This is broader: it includes the previous case, plus `rewards.restaurant` directly and deeper nestings too.

```
execution(* *..restaurant.*.*(..))
```
Here the package starts with a leading `*` instead. This is necessary because an expression can't validly *start* with `..` — so instead, you need something (`*`) before `..restaurant`. This matches any package ending in `restaurant`, with zero or more segments before it — `something.restaurant`, `something.something.restaurant`, and so on. This is the broadest of the three, and contains the second as a special case.

## Recap

- Spring AOP pointcut expressions center on the `execution` designator, because Spring AOP join points are always method invocations; the full AspectJ language is broader, but Spring AOP's subset covers the large majority of real cases.
- The method pattern is `[Modifiers] ReturnType [ClassType] MethodName(Arguments) [throws ExceptionType]` — only the return type and the method name with its arguments are required.
- `*` matches exactly one thing (a type, package segment, method name, or argument); `..` matches zero or more (arguments or package segments).
- You can match by a concrete class (which also matches its subclasses), by an interface (matching every implementation), or by annotation (ideal when there's no naming convention).
- Package wildcarding has three flavors of increasing breadth: `*` (exactly one segment), `..` (zero or more segments in the middle), and a leading `*` before `..` (since an expression can't start with `..`).
- Because these expressions are plain strings, always use fully qualified names for any non-primitive type, class, or annotation.

## Check your understanding

1. Write a pointcut expression that matches any method named `process`, with exactly one argument, on any class in the package `com.acme.billing`, returning any type.
2. What's the difference in meaning between `execution(* rewards.*.restaurant.*.*(..))` and `execution(* rewards..restaurant.*.*(..))`, and which one is broader?
3. Why can't a pointcut expression's package portion start with `..`, and what do you write instead to express "any number of leading packages"?

You've now seen how to define exactly *where* an aspect applies. Next, we'll look at the different types of advice you can attach to a pointcut — beyond the `@Before` advice you've used so far — and when each one is the right tool for the job.
