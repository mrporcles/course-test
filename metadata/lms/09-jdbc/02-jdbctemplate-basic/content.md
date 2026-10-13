## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Wire a `JdbcTemplate` into a repository through constructor injection
- Use `queryForObject` to query for simple Java types like `int`, `long`, `String`, and `Date`
- Pass bind variables to a query using `queryForObject`'s variable argument list
- Use `update` to run inserts, updates, and deletes, and know when to reach for `execute` instead

## A repository built on `JdbcTemplate`

Now that you've seen why `JdbcTemplate` exists (the "Problems with traditional JDBC and into JdbcTemplate" lesson), this lesson looks at its basic usage in practice.

```java
public class JdbcCustomerRepository implements CustomerRepository {

    private JdbcTemplate jdbcTemplate;

    public JdbcCustomerRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public int getCustomerCount() {
        String sql = "select count(*) from customer";
        return jdbcTemplate.queryForObject(sql, Integer.class);
    }
}
```

Notice that the `JdbcTemplate` is passed in through the constructor and stored in a field, so it can be reused across every method in the class. Recall from the "Problems with traditional JDBC and into JdbcTemplate" lesson that `JdbcTemplate` is thread-safe once constructed — there's no need to create a new one per method, or even per repository; one instance, typically a Spring-managed bean, can be shared everywhere.

Look at `getCustomerCount()`: there's no `try`/`catch`, no boilerplate — just a single line that gets data from the database. This uses `queryForObject`, passing the SQL statement and the type you expect back (here, `Integer`). Notice there's no JDBC API and no exception handling visible anywhere in this repository. That doesn't mean exceptions can't happen — if something goes wrong, an exception will still be thrown — it just means `JdbcTemplate` takes care of handling it, which is covered in the next module on exception handling.

## What `JdbcTemplate` can query for

`JdbcTemplate` can query for three broad categories of result:

- **Simple types** — `int`, `long`, `String`, `Date`, and similar
- **Generic maps** — and more generally, generic collections such as lists and maps
- **Domain objects** — your own mapped classes

This lesson focuses on the first category: querying for simple types.

## Querying for simple types

The method to reach for is `queryForObject`, passing the SQL statement and the type you expect back:

```java
public Date getOldest() {
    String sql = "select min(dob) from PERSON";
    return jdbcTemplate.queryForObject(sql, Date.class);
}

public long getPersonCount() {
    String sql = "select count(*) from PERSON";
    return jdbcTemplate.queryForObject(sql, Long.class);
}
```

`getOldest()` passes a query for the minimum date of birth and expects a `Date` back — no casting, nothing else needed. `getPersonCount()` follows the identical shape but expects a `Long`. Both are one-liners; all the boilerplate is handled by the template.

Older alternatives like `queryForInt()` and `queryForLong()` used to exist for this purpose, but they're deprecated and were removed as of Spring 4.2 — `queryForObject` with an explicit type is the method to use now.

## Querying with bind variables

Passing variables into the SQL statement works exactly the way it does in traditional JDBC — that hasn't changed, since this is still JDBC under the hood.

```java
private JdbcTemplate jdbcTemplate;

public int getCountOfNationalsOver(Nationality nationality, int age) {
    String sql = "select count(*) from PERSON " +
                 "where age > ? and nationality = ?";

    return jdbcTemplate.queryForObject
        (sql, Integer.class, age, nationality.toString());
}
```

The SQL statement uses question marks to mark bind variable positions, exactly as in plain JDBC. When calling `queryForObject`, after the SQL statement and the expected return type, you pass the variables to bind — in order, matching each `?` in the statement. Here, `age` binds to the first `?` and `nationality.toString()` binds to the second. This works through `queryForObject`'s variable argument list, so you can pass as many bind values as your query needs.

## Writing to the database: `update`

Can `JdbcTemplate` write data too? Yes — inserts, updates, and deletes are all supported, but there's no separate "insert" method. A single method, `update`, is used for all three.

**Inserting a row:**

```java
public int insertPerson(Person person) {
    return jdbcTemplate.update(
        "insert into PERSON (first_name, last_name, age)" +
        "values (?, ?, ?)",
        person.getFirstName(),
        person.getLastName(),
        person.getAge());
}
```

Three bind variables are defined in the SQL, and the three matching values are passed after it. `update` returns an `int` — the number of rows modified, which in this case would be `1`.

**Updating a row:**

```java
public int updateAge(Person person) {
    return jdbcTemplate.update(
        "update PERSON set age=? where id=?",
        person.getAge(),
        person.getId());
}
```

Same method, same shape: SQL statement first, followed by the values to bind. The same `update` method also handles deletes. In short: any non-`SELECT` SQL is run using `update()`.

There's also an `execute` method available for DDL operations (like creating or dropping tables), but for the everyday work of inserting, updating, and deleting rows, `update` is the one method you need.

## Recap

- A `JdbcTemplate`-based repository takes the template through constructor injection and stores it in a field, since it's thread-safe and meant to be reused.
- `queryForObject(sql, Type.class)` queries for a single simple value — a `Date`, `Long`, `Integer`, and so on — with no casting required.
- The older `queryForInt()` / `queryForLong()` methods are deprecated and were removed in Spring 4.2; use `queryForObject` instead.
- Bind variables work exactly like plain JDBC's `?` placeholders — pass the values, in order, as extra arguments to `queryForObject`.
- `update()` is the single method for inserts, updates, and deletes, returning the number of rows modified; `execute()` is reserved for DDL operations.

## Check your understanding

1. Why doesn't `getCustomerCount()` in the example repository need a `try`/`catch` block, even though the underlying call could fail?
2. If a query has two `?` placeholders, how do you tell `queryForObject` which values to bind to them, and in what order?
3. Which single `JdbcTemplate` method would you use to both insert a new row and later delete it, and what does it return?

The next lesson goes beyond simple types and looks at working with full result sets using callbacks like `RowMapper`.
