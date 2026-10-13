## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Define "cross-cutting concern," and recognize the word "every" in a requirement as a hint that you're looking at one
- Explain the two problems that show up when cross-cutting concerns aren't modularized: code tangling and code scattering
- Describe, at a high level, the three steps Aspect-Oriented Programming uses to eliminate those problems
- Compare AspectJ and Spring AOP, and know which one the rest of this course focuses on

## Introducing AOP

This module introduces **AOP**, Aspect-Oriented Programming — a genuinely important building block in Spring. The plan across this module: start with the concepts behind AOP and why it's needed, implement a first advice, and cover advices, aspects, and pointcut expressions using the AspectJ expression language. A later lesson finishes by covering the different types of advice available.

## What is a cross-cutting concern?

AOP exists to **modularize cross-cutting concerns**. A cross-cutting concern is a behavior that spans across your codebase — you see the same behavior repeated across multiple classes and modules. In Java, a class is normally how you modularize behavior, and the goal of AOP is to take a cross-cutting concern and pull it into its own module (its own class), separate from everything else. Common examples: logging, transactions, security, and caching — behaviors you need practically everywhere in an application, not just in one place.

Here's a hint for spotting one: "Perform a role-based security check before **every** application method." That word — *every* — is the signal. Any time a requirement says something needs to happen everywhere, or in every method, you're probably looking at a cross-cutting concern that should be modularized rather than hand-coded into each place it's needed.

## Problem #1: code tangling

If you don't modularize a cross-cutting concern, you run into two distinct problems. The first is **code tangling** — the coupling, or mixing, of concerns. Your business logic ends up interleaved with security behavior, transactional behavior, error-handling behavior, and so on, all in the same method.

```java
public class RewardNetworkImpl implements RewardNetwork {
    public RewardConfirmation rewardAccountFor(Dining dining) {

        // Security-related code
        if (!hasPermission(SecurityContext.getPrincipal())) {
            throw new AccessDeniedException();
        }

        // Application code
        Account a = accountRepository.findByCreditCard(...);
        Restaurant r = restaurantRepository.findByMerchantNumber(...);
        MonetaryAmount amt = r.calculateBenefitFor(account, dining);
        ...
    }
}
```

Three lines of security-related code are now mixed directly into the business logic. That mixing makes the method harder to test — if you want to test just the reward-calculation logic, you now have to somehow deal with the security concern too, even though it's logically unrelated.

## Problem #2: code scattering

The second problem is **code scattering**. Since this particular requirement applies to *every* method, that same three-line security check ends up copied and pasted into every module that needs it.

```java
public class JpaAccountManager implements AccountManager {
    public Account getAccountForEditing(Long id) {
        if (!hasPermission(SecurityContext.getPrincipal())) {
            throw new AccessDeniedException();
        }
        ...
    }
}

public class JpaMerchantReportingService
        implements MerchantReportingService {
    public List<DiningSummary> findDinings(String merchantNumber,
                                            DateInterval interval) {
        if (!hasPermission(SecurityContext.getPrincipal())) {
            throw new AccessDeniedException();
        }
        ...
    }
}
```

Copy-pasting behavior like this is a warning sign. If you ever need to change how the security check works, you now have to hunt down and update every copy — and it's easy for those copies to drift out of sync with each other over time, so different modules end up enforcing the "same" concern slightly differently.

## Seeing both problems together

Zooming out, here's how a system evolves if cross-cutting concerns are never pulled out into their own modules:

![System Evolution Without Modularization](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/07-aop/01-what-aop-solve/images/lesson24-system-evolution-without-modularization.png)

Each of `BankService`, `CustomerService`, and `ReportingService` mixes its blue business logic together with security, transaction, and logging code. **Code scattering** is the same behavior appearing again in every module. **Code tangling** is what's happening *within* any one module — business logic, security, transactions, and logging all mixed together in the same component.

## How AOP solves it: three steps

AOP eliminates both of these problems with a three-step approach:

1. **Focus on the application logic.** Implement just the business logic — don't introduce security, transactions, or any other cross-cutting behavior at this point.
2. **Identify the cross-cutting concerns.** Do you need security? Transactions? Anything else that shows up in multiple places? Take each one and modularize it into its own **aspect**.
3. **Weave.** Combine the business logic and the aspects together — this mixing step is called **weaving**, and there are different techniques for actually doing it, which you'll see in later lessons.

Applying that to the same system:

![System Evolution: AOP based](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/07-aop/01-what-aop-solve/images/lesson24-system-evolution-aop-based.png)

The three services are now clean — just business logic. Security, Transaction, and Logging each become their own independent aspect, completely decoupled from the business logic and from each other. Weaving is what applies these aspects on top of the business logic at the right points.

## AspectJ vs. Spring AOP

There are two major AOP technologies worth knowing about:

- **AspectJ** — the original AOP technology (first released in 1995). It's a full-blown, standalone Aspect-Oriented Programming language. It weaves aspects in by modifying **bytecode**, a technique called **load-time weaving**: it rewrites the bytecode as classes are loaded into the classloader.
- **Spring AOP** — a Java-based AOP framework that integrates with AspectJ (you'll actually use AspectJ's *annotations* and *expression language*), but weaves aspects differently: it uses **dynamic proxies** instead of bytecode modification. It's generally simpler than full AspectJ, focuses specifically on solving enterprise problems, and requires no extra configuration to integrate with the Spring container.

For more detail, see the Spring Framework Reference, Aspect Oriented Programming: <a href="https://docs.spring.io/spring/docs/current/spring-framework-reference/core.html#aop" target="_blank" rel="noopener noreferrer">https://docs.spring.io/spring/docs/current/spring-framework-reference/core.html#aop</a>

This course focuses on Spring AOP going forward — you'll see exactly how the proxy-based weaving works in the next lesson.

Now that you know *why* AOP exists, the next lesson introduces the core vocabulary — join points, pointcuts, advice, aspects, and weaving — and walks through building your first working aspect with Spring AOP.
