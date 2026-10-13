## What you'll get out of this lesson

By the end of this lesson, you should be able to:

- Use `queryForMap` and `queryForList` to get raw, unmapped rows back as generic maps
- Explain when you'd reach for `JdbcTemplate`'s mapping support instead of a full ORM
- Implement a `RowMapper` to map one row of a `ResultSet` into a domain object, for both single- and multi-row queries
- Implement a `ResultSetExtractor` to map an entire `ResultSet` into a single object
- Explain how `RowCallbackHandler` differs from `RowMapper`

## Beyond simple values

the "JdbcTemplate Basic Usage" lesson showed a fairly basic use of `JdbcTemplate`: pulling a single simple value — a count of customers — out of a `ResultSet`. Most of the time you need more than that: a query returns a bunch of rows with a bunch of columns, and you need a way to work with that whole shape of data. This lesson covers two ways of doing that: mapping straight into generic collections, and mapping into your own domain objects using callbacks.

## Option 1: Querying into generic maps

One option is to map the `ResultSet` directly into a collection — a `Map` or a `List` — without mapping anything into your own domain objects. You get the raw data back, with no notion of your own classes involved at all.

Two methods are available, depending on how many rows you expect:

- **`queryForMap(...)`** — for a single row
- **`queryForList(...)`** — for multiple rows

This is particularly useful for **ad hoc** queries (queries created or done for a particular purpose as necessary — sometimes called "window-on-data" queries), for testing, or any time you just want to peek at what's inside a table without the ceremony of mapping to a Java object.

### Querying for a single row: `queryForMap`

```java
public Map<String,Object> getPersonInfo(int id) {
    String sql = "select * from PERSON where id=?";
    return jdbcTemplate.queryForMap(sql, id);
}
```

This returns a `Map` of key-value pairs, where each key is a column name and each value is that column's value for the row:

```
Map { ID=1, FIRST_NAME="John", LAST_NAME="Doe" }
```

### Querying for multiple rows: `queryForList`

```java
public List<Map<String,Object>> getAllPersonInfo() {
    String sql = "select * from PERSON";
    return jdbcTemplate.queryForList(sql);
}
```

This returns a list of maps — one map per row, in the same column-name-to-value shape as before:

```
List {
  0 - Map { ID=1, FIRST_NAME="John", LAST_NAME="Doe" }
  1 - Map { ID=2, FIRST_NAME="Jane", LAST_NAME="Doe" }
  2 - Map { ID=3, FIRST_NAME="Junior", LAST_NAME="Doe" }
}
```

Be careful using `queryForList` against a query that returns a lot of rows — building a map for every single row is memory-intensive, so it's a better fit for smaller or bounded result sets.

## Option 2: Mapping into domain objects

Often it's useful to map relational data directly into domain objects — for example, mapping a `ResultSet` row into an `Account`. This is exactly what an ORM does, but you don't always need a full ORM to get this behavior. `JdbcTemplate` supports mapping into domain objects itself, using a callback approach, with three callback interfaces covered in this lesson.

To be clear, this isn't a replacement for an ORM — an ORM gives you far more than row-to-object mapping, including a first-level cache, a second-level cache, an object query language, and more. But when you have a particularly complex schema (heavy joins, tables that are awkward to map with JPA or a similar tool), reaching for `JdbcTemplate`'s mapping support instead of forcing an ORM mapping can be the simpler, more direct choice.

### Callback 1: `RowMapper`

`RowMapper` maps a single row of a `ResultSet` into an object. It can be used for both single-row and multi-row queries, and is parameterized to define its return type.

```java
public interface RowMapper<T> {
    T mapRow(ResultSet rs, int rowNum) throws SQLException;
}
```

It's a functional interface with a single method, `mapRow`. You'd define one mapper implementation per type you want to map — one for `Customer`, one for `Employee`, one for `Order`, and so on. Your job is only to know how to translate the *current* row into an object; if there are multiple rows, `JdbcTemplate` itself iterates the `ResultSet` and invokes your callback once per row, always positioned at the current row.

**Querying for a single row** uses `queryForObject`, with the `RowMapper` written as a lambda:

```java
public Person getPerson(int id) {
    return jdbcTemplate.queryForObject(
        "select first_name, last_name from PERSON where id=?",
        (rs, rowNum) -> new Person(rs.getString("first_name"),
                                    rs.getString("last_name")),
        id);
}
```

The functional interface is expressed here as a lambda: given the current row, build a `Person` from the `first_name` and `last_name` columns. The bind variable (`id`) is passed after the callback.

**Querying for multiple rows** uses `query` instead of `queryForObject`, but the same `RowMapper` lambda:

```java
public List<Person> getAllPersons() {
    return jdbcTemplate.query(
        "select first_name, last_name from PERSON",
        (rs, rowNum) -> new Person(rs.getString("first_name"),
                                    rs.getString("last_name")));
}
```

`JdbcTemplate` iterates over the full `ResultSet`, invoking the callback for every row and collecting each returned `Person` into the list it hands back. (For a longer or more complex mapping, you could pull the lambda out into its own `RowMapper` implementation and pass it as a method reference instead — either style works.)

### Callback 2: `ResultSetExtractor`

The second callback, `ResultSetExtractor`, differs from `RowMapper` in one key way: instead of a one-to-one mapping (one row in, one object out), it's an **n-to-one** mapping — you get the *entire* `ResultSet`, you're responsible for iterating it yourself, and you return a single object built from everything you saw.

```java
public interface ResultSetExtractor<T> {
    T extractData(ResultSet rs) throws SQLException, DataAccessException;
}
```

This is useful for cases like joining multiple tables, where several rows in the `ResultSet` really represent one logical object (an order with several line items, for example).

**Using a `ResultSetExtractor`**:

```java
public class JdbcOrderRepository {
    public Order findByConfirmationNumber(String number) {
        // Execute an outer join between order and item tables
        return jdbcTemplate.query(
            "select...from order o, item i...confirmation_id = ?",
            (ResultSetExtractor<Order>)(rs) -> {
                Order order = null;
                while (rs.next()) {
                    if (order == null)
                        order = new Order(rs.getLong("ID"), rs.getString("NAME"), ...);
                    order.addItem(mapItem(rs));
                }
                return order;
            },
            number);
    }
}
```

This still uses the same `query` method on `JdbcTemplate` — only the callback type changes. Notice the explicit cast to `ResultSetExtractor<Order>` on the lambda: unlike `RowMapper` (which has a unique method signature), several `JdbcTemplate` callbacks share a `ResultSet`-based signature, so the compiler needs the cast to know which one you mean. Inside, you manually call `rs.next()` in a loop, building up the single `Order` (and its line items) as you go, and return it once the loop finishes iterating the whole `ResultSet`.

### Callback 3: `RowCallbackHandler`

A third callback, `RowCallbackHandler`, behaves like `RowMapper` in that you get access to every row in the `ResultSet` — but you don't return anything from it. That makes it a good fit for streaming data out somewhere else (writing rows to a file, for instance) or otherwise just processing each row as a side effect, without needing to build up and return a mapped result.

## Summary of the three callbacks

- **`RowMapper`** — best choice when *each* row of a `ResultSet` maps to a domain object.
- **`ResultSetExtractor`** — best choice when *multiple* rows of a `ResultSet` map to a *single* object.
- **`RowCallbackHandler`** — yet another handler, one that writes to alternative destinations rather than returning a mapped result.

The next lesson turns to exception handling — specifically, how `JdbcTemplate` translates the checked `SQLException` you saw in the "Problems with traditional JDBC and into JdbcTemplate" lesson into something more useful to work with.
