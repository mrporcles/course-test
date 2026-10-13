## What you'll get out of this lesson

This lesson walks through a hands-on lab that takes an existing, working codebase built on plain JDBC and refactors it, method by method, to use `JdbcTemplate`. By the end, you should be able to:

- Replace hand-written `Connection`/`PreparedStatement`/`ResultSet` boilerplate with `JdbcTemplate`'s `queryForObject`, `queryForMap`, `query`, and `update` methods
- Pass a `RowMapper` lambda to map a single row into an object, and recognize when to use a method reference instead
- Pass a `ResultSetExtractor` to map an entire result set into a single object
- Migrate a class's dependency from a raw `DataSource` to an injected `JdbcTemplate`, and update both the Spring configuration and the tests that construct it

## The scenario

This lab is pure refactoring. The starting codebase (project 26, "JDBC") already works — every repository method executes correctly against the database, but they all go through the plain JDBC API by hand: acquire a `Connection` from the `DataSource`, create a `PreparedStatement`, set its parameters, execute the query, walk the `ResultSet`, and finally close everything. The goal is to strip all of that down using `JdbcTemplate` and, where a full row or result set needs mapping, its two callback interfaces — `RowMapper` and `ResultSetExtractor`.

As is typical for these labs, the work is organized as a series of numbered to-dos, and the walkthrough below follows that same structure — to-dos 1–6 are required, and to-dos 7–10 are optional but demonstrate the rest of the technique.

## To-dos 1–2: Getting comfortable with `JdbcTemplate` in a test class

The first two to-dos live in a test class that already has a `JdbcTemplate` configured in its `beforeEach` method — the point here is just to get familiar with the template's basic methods before touching real repository code.

**To-do 1** asks for the number of rows in the `T_REWARD` table. Since the result is a single scalar value, this is a job for `queryForObject`, passing the SQL statement as the first argument and the expected return type as the second:

```java
Integer count = jdbcTemplate.queryForObject(sql, Integer.class);
```

**To-do 2** asks for every column of a single row in `T_REWARD`, identified by confirmation number. Because this is a `SELECT *` returning multiple columns from a single row, `queryForObject` isn't the right tool — instead, `queryForMap` returns that row's columns as a `Map`. Values to bind into the SQL statement's placeholders are passed as trailing arguments, after the SQL itself:

```java
Map<String, Object> row = jdbcTemplate.queryForMap(sql, confirmationNumber);
```

Running the test class after these two changes confirms both methods were used correctly.

## To-do 3: Refactoring `JdbcRewardRepository`

This is where the real refactoring starts. `JdbcRewardRepository`, like the other repositories in this codebase, has a constructor that accepts a `DataSource`, and every method inside it manually acquires a connection, builds a `PreparedStatement`, sets parameters by index, and executes.

The first step is adding a `JdbcTemplate` field and initializing it inside the existing constructor, without changing the constructor's signature:

```java
private JdbcTemplate jdbcTemplate;

public JdbcRewardRepository(DataSource dataSource) {
    this.dataSource = dataSource;
    this.jdbcTemplate = new JdbcTemplate(dataSource);
}
```

The constructor still accepts a `DataSource` at this point rather than a `JdbcTemplate` directly — deliberately. Changing the constructor's contract to accept a `JdbcTemplate` instead is saved for the optional to-dos later in this lab, so as not to leak that implementation detail before it's needed.

With the template in place, two methods get refactored:

- **`confirmReward`** performs an `INSERT` into `T_REWARD` with seven parameters. Since `JdbcTemplate` has no dedicated "insert" method, inserts, updates, and deletes all go through the same `update` method — the SQL statement first, followed by each bound parameter as a trailing argument, in order:

  ```java
  jdbcTemplate.update(sql,
      confirmationNumber, accountNumber, dining.getAmount(),
      dining.getDate(), merchantNumber, dining.getCreditCardNumber(),
      accountContribution.getAmount());
  ```

  A useful tactic here: don't delete the old plain-JDBC code until the new line is written and verified — the original code is the easiest reference for which value belongs in which position.

- **`nextConfirmationNumber`** retrieves a single string value, which maps directly onto `queryForObject`, returning `String.class` and letting the result flow straight back through a `return` statement instead of an intermediate variable.

Re-running the `JdbcRewardRepository` test class after these changes confirms both methods still behave correctly.

## To-do 4: Refactoring `JdbcRestaurantRepository` with a `RowMapper`

The same pattern — add a `JdbcTemplate` field, initialize it in the constructor from the injected `DataSource` — applies again here. The interesting part of this to-do is `findByMerchantNumber`, which needs to map a single row from `T_RESTAURANT` into a `Restaurant` object.

`JdbcTemplate`'s `queryForObject` method has an overload that accepts a **`RowMapper`** as a callback instead of a simple `Class`. `RowMapper` is a functional interface with a single method that receives a `ResultSet` and a row number, and returns a mapped object — which makes it a natural fit for a lambda. Conveniently, the mapping logic itself (`mapRestaurant`) already exists elsewhere in the class, so the lambda just needs to delegate to it:

```java
Restaurant restaurant = jdbcTemplate.queryForObject(sql,
    (rs, rowNum) -> mapRestaurant(rs), merchantNumber);
```

Since the lambda's signature exactly matches `mapRestaurant`'s own signature, it can be simplified further into a plain method reference:

```java
Restaurant restaurant = jdbcTemplate.queryForObject(sql,
    this::mapRestaurant, merchantNumber);
```

With the callback in place, the old manual connection/statement/result-set code — and a helper method that existed only to support it — can both be deleted outright. Re-running `JdbcRestaurantRepositoryTest` confirms the refactor holds up.

## To-do 5: Setting up `JdbcAccountRepository`

This to-do is just the setup half of the pattern repeated once more: add a `JdbcTemplate` field to `JdbcAccountRepository` and initialize it from the `DataSource` in the constructor. The method refactoring itself is split across to-dos 6 and 7.

## To-do 6: Refactoring `updateBeneficiaries`

An account can have multiple beneficiaries, and the existing `updateBeneficiaries` method loops over all of them, issuing a manual JDBC update for each one. The refactor keeps the loop, but swaps the body for a call to `jdbcTemplate.update`, passing the three bound parameters that update statement needs:

```java
for (Beneficiary beneficiary : account.getBeneficiaries()) {
    jdbcTemplate.update(sql,
        beneficiary.getSavings(), account.getNumber(), beneficiary.getName());
}
```

All of the old manual connection-handling code, along with variables that are no longer referenced once it's removed, gets deleted. Re-running `JdbcAccountRepositoryTest` confirms the beneficiaries still update correctly.

## To-do 7 (optional): A `ResultSetExtractor` for `findByCreditCard`

This to-do introduces `JdbcTemplate`'s other major callback interface. Where `RowMapper` maps *one row at a time* (a one-to-one mapping), **`ResultSetExtractor`** maps an *entire result set* into a single object (many-to-one) — the right tool when a full `Account`, built from multiple rows or a more involved read of the cursor, needs to come back as one object.

![The ResultSetExtractor functional interface, showing its single extractData(ResultSet) method](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/09-jdbc/06-jdbctemplate-lab-demo/images/lesson37-resultsetextractor-interface.png)

`ResultSetExtractor` is a functional interface with a single method that takes the `ResultSet` and returns the fully mapped object — in this case an `Account`. As with the row mapper before it, the mapping logic already exists in this class as `mapAccount`, so a method reference is enough:

```java
Account account = jdbcTemplate.query(sql, this::mapAccount, creditCardNumber);
```

Note this uses `query`, not `queryForObject` — `ResultSetExtractor` is passed to `query`. Once this is wired up, the method's old manual JDBC code can be removed and the result returned directly. Re-running `JdbcAccountRepositoryTest` confirms the account is still mapped correctly.

![Mid-refactor view of a repository: the old plain-JDBC block still visible alongside the new jdbcTemplate.query call using a row-mapper lambda](https://raw.githubusercontent.com/mrporcles/course-test/main/metadata/lms/09-jdbc/06-jdbctemplate-lab-demo/images/lesson37-refactoring-to-jdbctemplate.png)

## To-dos 8–10 (optional): Injecting `JdbcTemplate` directly

The remaining to-dos revisit the deliberate choice made back in to-do 3: keeping each repository's constructor accepting a `DataSource`, and building the `JdbcTemplate` internally. These to-dos undo that, one repository at a time (reward, then restaurant, then account) — changing each constructor to accept a `JdbcTemplate` directly instead:

```java
public JdbcRewardRepository(JdbcTemplate jdbcTemplate) {
    this.jdbcTemplate = jdbcTemplate;
}
```

Each change ripples outward in the same two places:

- **The Spring configuration** (`RewardsConfig`) needs its own `JdbcTemplate` bean, built from the injected `DataSource`, and each repository's bean definition needs updating to pass that `JdbcTemplate` bean in instead of the raw `DataSource`.
- **Each repository's test class** needs to construct its own `JdbcTemplate` from the `DataSource` already available in the test, and pass that into the repository's constructor instead.

After each of the three repositories is migrated this way, re-running that repository's test class confirms everything still passes — proving the constructor's contract can change cleanly as long as every caller (both the production configuration and the tests) is updated to match.

With the JDBC module now complete, next up is the **module quiz**, where you can check your understanding of everything covered here. After the quiz, the course turns to a new topic: why transactions matter, and how Spring manages them for you.
