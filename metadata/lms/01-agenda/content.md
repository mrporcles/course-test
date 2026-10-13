## What you'll get out of this lesson

This first lesson is an orientation, not a technical deep-dive. By the end of it, you should be able to:

- Explain what this course covers and in what order
- Understand the mixture of theory and hands-on labs you'll be working through
- Recognize the range of application types Spring can be used to build
- Know the history behind Spring's relationship with VMware and Broadcom

## Welcome to Spring Essentials

This training focuses on plain, "vanilla" Spring — the core framework itself, before any Spring Boot auto-configuration is layered on top. You'll learn the basics and the main building blocks in a practical way, with a solid mixture of presentation and hands-on labs.

For the labs, you'll work with a real-world application called the reward network. Its business logic is already implemented, and across the course you'll progressively add configuration, aspects, tests, a data-access layer, and more to it — rather than starting from scratch every time.

## The course agenda

The training is organized into two broad parts.

The first part is focused on the Spring container — also called the application context. You'll start with an introduction to Spring itself, then move into configuring the application context. You'll see different configuration styles, such as Java configuration and annotation-based configuration. (XML configuration won't be covered — the industry has been moving away from it for some time.) You'll also learn about the bean lifecycle: how the container manages your components through their initialization, use, and destruction phases.

The topics in this first part are, in order:

- **Introduction to Spring** — what the framework is and what it gives you.
- **Using Spring to configure an application** — setting up the application context.
- **Java-based dependency injection** — Java configuration, one of the main configuration styles.
- **Component-scanning with annotated classes** — annotation-based configuration, the other main style.
- **Inside the Spring container** — how the container works under the hood.
- **The bean lifecycle and its related post processors** — how your components are initialized, used and destroyed.

The second part builds on that foundation:

- **Aspect-Oriented Programming (AOP)** — one of Spring's core building blocks. You'll implement your first aspect, and even if you never write an aspect yourself, you'll be relying on AOP any time you use transactions, security, or caching in Spring — this is also where the concept of proxies gets introduced.
- **Testing** — testing is essential, and you'll test both your application code and your application context using JUnit 5 and Spring's test context framework.
- **The data access layer** — you'll see how Spring simplifies the JDBC API, including the `JdbcTemplate`, and how to drive database transactions with Spring's transaction support.

## What can Spring do?

Spring makes programming Java quicker, easier, and safer, and it can be used to build almost any type of application:

- **Microservices** — quickly deliver production-grade features with independently evolvable services
- **Reactive** — asynchronous, non-blocking architectures that get more out of your computing resources
- **Cloud** — connect and scale your services on whatever platform you use
- **Web apps** — from simple REST APIs to server-side rendered templates
- **Event Driven** — integrating with middleware like RabbitMQ or Kafka
- **Batch** — automated, offline processing of data
- **Serverless** — thanks to support for GraalVM and native compilation, Spring applications can scale to zero when there's no demand

If you want to explore the full portfolio of Spring projects, <a href="https://spring.io/projects" target="_blank" rel="noopener noreferrer">https://spring.io/projects</a> is worth bookmarking.

## A short history lesson: Spring, VMware and Broadcom

You don't need this to write code, but it explains some of the branding you'll run into in documentation and tooling:

- **2003** — the Spring Framework is released as an open source project (version 0.9); version 1.0 follows in 2004.
- **2004** — a company is formed to support the framework: **Interface21**.
- **2007** — Interface21 is renamed **SpringSource**.
- **2009** — SpringSource is acquired by **VMware**.
- **2013** — VMware and its parent, EMC, spin Spring out into a joint venture, **Pivotal**.
- **2019** — **VMware re-acquires Pivotal**, bringing Spring back under VMware, where it becomes part of the Tanzu portfolio.
- **2023** — **Broadcom completes its acquisition of VMware**, and Spring is now developed by VMware by Broadcom.
- **2025** — Spring Framework 7.0 and Spring Boot 4.0 are released.
- **2026** — Broadcom announces an expanded investment in the security of Spring and the Java ecosystem, with enterprise support delivered through VMware Tanzu Spring.

So when you see "VMware Spring", "VMware Tanzu" or "Broadcom" in official material, now you know why: Spring has been through several owners, and today its development is led by VMware, part of Broadcom. Spring itself remains open source under the Apache 2 license.

Let's get on with the course — next up is **What is the Spring Framework?**, where you'll take a closer look at what the Spring Framework actually is.
