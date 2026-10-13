## What you'll get out of this lesson

This first lesson is an orientation, not a technical deep-dive. By the end of it, you should be able to:

- Explain what this course covers and in what order
- Understand the mixture of theory and hands-on labs you'll be working through
- Recognize the range of application types Spring can be used to build
- Know the history behind Spring's relationship with VMware

## Welcome to Spring Essentials

This training focuses on plain, "vanilla" Spring — the core framework itself, before any Spring Boot auto-configuration is layered on top. You'll learn the basics and the main building blocks in a practical way, with a solid mixture of presentation and hands-on labs.

For the labs, you'll work with a real-world application called the reward network. Its business logic is already implemented, and across the course you'll progressively add configuration, aspects, tests, a data-access layer, and more to it — rather than starting from scratch every time.

## The course agenda

The training is organized into two broad parts.

The first part is focused on the Spring container — also called the application context. You'll start with an introduction to Spring itself, then move into configuring the application context. You'll see different configuration styles, such as Java configuration and annotation-based configuration. (XML configuration won't be covered — the industry has been moving away from it for some time.) You'll also learn about the bean lifecycle: how the container manages your components through their initialization, use, and destruction phases.

![Course Agenda, part 1](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/01-agenda/images/lesson1-agenda-part1.png)

The second part builds on that foundation:

- **Aspect-Oriented Programming (AOP)** — one of Spring's core building blocks. You'll implement your first aspect, and even if you never write an aspect yourself, you'll be relying on AOP any time you use transactions, security, or caching in Spring — this is also where the concept of proxies gets introduced.
- **Testing** — testing is essential, and you'll test both your application code and your application context using JUnit 5 and Spring's test context framework.
- **The data access layer** — you'll see how Spring simplifies the JDBC API, including the `JdbcTemplate` and Spring's transaction support.

![Course Agenda, part 2](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/01-agenda/images/lesson1-agenda-part2.png)

## What can Spring do?

Spring makes programming Java quicker, easier, and safer, and it can be used to build almost any type of application:

- **Microservices** — quickly deliver production-grade features with independently evolvable services
- **Reactive** — asynchronous, non-blocking architectures that get more out of your computing resources
- **Cloud** — connect and scale your services on whatever platform you use
- **Web apps** — from simple REST APIs to server-side rendered templates
- **Event Driven** — integrating with middleware like RabbitMQ or Kafka
- **Batch** — automated, offline processing of data
- **Serverless** — thanks to support for GraalVM and native compilation, Spring applications can scale to zero when there's no demand

If you want to explore the full portfolio of Spring projects, `https://spring.io/projects` is worth bookmarking.

## A short history lesson: Spring and VMware

You don't need this to write code, but it explains some of the branding you'll run into in documentation and tooling:

- **2004** — a company was formed to support the Spring Framework, which had come out in late 2003/early 2004. That company was called Interface21, later renamed **SpringSource**.
- **2009** — SpringSource was acquired by **VMware**.
- **2013** — VMware transferred Spring to a spin-off joint venture called **Pivotal**.
- **2019** — **VMware re-acquired Pivotal**, bringing Spring development back under VMware.

So when you see "VMware Spring" or "VMware Tanzu" in official material, now you know why: all Spring development today is done by VMware, which is the framework's current home.

## Recap

- This course teaches plain Spring — dependency injection, configuration, AOP, testing, and JDBC support — without relying on Spring Boot's auto-configuration.
- The labs build up a single real-world application (the reward network) piece by piece, rather than using disconnected examples.
- Spring can be used to build almost any kind of application: microservices, reactive systems, cloud-native apps, web apps, event-driven systems, batch jobs, and even serverless functions.
- Spring's development today is done by VMware, following a path from Interface21 → SpringSource → VMware → Pivotal → back to VMware.

## Check your understanding

1. What are the two broad parts this course is organized into, and what does each one cover?
2. Name three different types of applications you could build with Spring.
3. What company originally created Spring, and what path did it take to end up back at VMware?

Let's get on with the course — next up is **What is the Spring Framework?**, where you'll take a closer look at what the Spring Framework actually is.
