# C++ Fundamentals — Memory, Pointers, References & Functions

> Interview-focused refresher.
> These notes assume the reader has learned C++ before but may be revisiting it after a long gap.

---

# 1. Modern C++ Program Structure

A basic C++ program often starts with:

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Hello";
    return 0;
}
```

There are several separate concepts here.

---

## 1.1 `#include <iostream>`

```cpp
#include <iostream>
```

`#include` is a **preprocessor directive**.

It tells the preprocessor to make the contents/declarations provided by the `iostream` header available to the source file.

`iostream` provides standard input/output facilities such as:

```cpp
cout
cin
cerr
```

Example:

```cpp
#include <iostream>

int main() {
    std::cout << "Hello";
}
```

### Important

`#include <iostream>` does **not** have a semicolon.

It is not a normal C++ statement.

---

## 1.2 Old `iostream.h` vs modern `iostream`

Older C++ code may contain:

```cpp
#include <iostream.h>
```

Modern standard C++ uses:

```cpp
#include <iostream>
```

Similarly, old code may contain:

```cpp
#include <conio.h>
```

`conio.h` is associated with older/non-standard compiler environments and is not part of standard modern C++.

C's traditional I/O header is:

```cpp
#include <stdio.h>
```

Modern C++ can also use the C-compatible form:

```cpp
#include <cstdio>
```

For current C++ interview preparation, prefer the standard C++ headers:

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <set>
#include <queue>
#include <stack>
```

---

# 2. Namespace and `std`

The C++ standard library places its names inside a namespace called:

```cpp
std
```

Therefore:

```cpp
std::cout
std::string
std::vector
std::set
```

The `::` operator means:

> Access a name inside a namespace/class/etc.

So:

```cpp
std::cout
```

means:

> `cout` belonging to the `std` namespace.

---

## 2.1 `using namespace std;`

```cpp
using namespace std;
```

This allows us to write:

```cpp
cout
string
vector
```

instead of:

```cpp
std::cout
std::string
std::vector
```

For example:

```cpp
#include <iostream>

int main() {
    std::cout << "Hello";
}
```

is equivalent, in this context, to:

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Hello";
}
```

### Important

These are **separate concepts**:

```cpp
#include <iostream>
using namespace std;
```

`#include` makes the header available.

`using namespace std;` allows names from `std` to be written without `std::`.

Neither requires the other.

This is valid:

```cpp
#include <iostream>

int main() {
    std::cout << "Hello";
}
```

And this is also valid:

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Hello";
}
```

---

# 3. Semicolons

A very important C++ rule:

> Normal C++ declarations/statements usually end with `;`, but not every line of a C++ program is a statement.

Examples:

```cpp
int x = 10;              // ;
x = 20;                  // ;
cout << x;               // ;

using namespace std;     // ;

#include <iostream>      // no ;
```

A function declaration/definition does not put a semicolon after the function body:

```cpp
int main() {
    return 0;
}
```

However, a class definition normally does:

```cpp
class Student {
};
```

The semicolon after the closing `}` is required.

---

# 4. Variables and Memory

Consider:

```cpp
int x = 10;
```

`x` is a variable containing the value `10`.

Every object/variable occupies storage somewhere in the program's memory.

For interview purposes, think of memory using a simplified model:

```text
Program memory
├── Code
├── Global/static data
├── Heap
└── Stack
```

The exact physical implementation is managed by the operating system/compiler/runtime, and the C++ standard does not require every implementation to use exactly this physical layout.

For our interview mental model:

* local automatic variables → typically associated with the stack
* dynamically allocated objects → typically associated with the heap

---

# 5. Address-of Operator `&`

Given:

```cpp
int x = 10;
```

we can obtain its address:

```cpp
&x
```

Read this as:

> "the address of `x`"

Example:

```cpp
cout << x;
cout << &x;
```

Conceptually:

```text
x
┌──────┐
│  10  │
└──────┘
   ↑
   |
 address of x = &x
```

The actual address is not important for understanding the concept.

---

# 6. Pointers

A pointer is a variable that stores an address.

```cpp
int x = 10;
int* p = &x;
```

Here:

```text
x = 10

p = address of x
```

Conceptually:

```text
STACK

x
┌──────┐
│  10  │
└──────┘

p
┌──────────────┐
│ address of x │
└──────────────┘
```

The declaration:

```cpp
int* p;
```

means:

> Create a pointer variable `p` capable of storing the address of an `int`.

It does not automatically make `p` point to a valid integer.

---

# 7. Dereference Operator `*`

If:

```cpp
int x = 10;
int* p = &x;
```

then:

```cpp
*p
```

means:

> Go to the address stored in `p` and access the value there.

Therefore:

```cpp
cout << *p;
```

prints:

```text
10
```

---

## 7.1 Modifying a value through a pointer

```cpp
int x = 10;
int* p = &x;

*p = 20;
```

`p` points to `x`, so changing `*p` changes `x`.

After:

```cpp
*p = 20;
```

we have:

```text
x = 20
```

Mental model:

```text
p ─────────► x
              10

*p = 20

p ─────────► x
              20
```

---

# 8. `p` vs `*p`

This distinction is fundamental.

Given:

```cpp
int x = 10;
int* p = &x;
```

### `p`

```cpp
p
```

means:

> The address currently stored inside the pointer.

### `*p`

```cpp
*p
```

means:

> The value at the address stored in `p`.

So:

```text
p   → address
*p  → value at that address
```

---

# 9. Pointer Can Be Redirected

A pointer can point to different objects.

```cpp
int x = 10;
int y = 50;

int* p = &x;
```

Initially:

```text
p ─────► x
```

Then:

```cpp
p = &y;
```

Now:

```text
p ─────► y
```

The pointer changed what it points to.

This is one of the major differences between a pointer and a reference.

---

# 10. References

A reference is an **alias for an existing object**.

```cpp
int x = 10;

int& r = x;
```

Read it as:

> `r` is a reference to `x`.

Conceptually:

```text
      ┌──────┐
x ───►│  10  │
r ───►│      │
      └──────┘
```

There are not two separate integers.

`r` is another name for the same object.

---

# 11. Reference Modification

Given:

```cpp
int x = 10;
int& r = x;

r = 20;
```

`r` refers to `x`, therefore:

```text
x = 20
```

No error occurs.

---

# 12. Pointer vs Reference

## Pointer

```cpp
int x = 10;
int* p = &x;
```

Mental model:

```text
p → stores address of x
```

A pointer:

* is a separate variable
* stores an address
* can be redirected
* can represent `nullptr`
* uses `*` for dereferencing

---

## Reference

```cpp
int x = 10;
int& r = x;
```

Mental model:

```text
r → another name for x
```

A reference:

* acts as an alias
* must be initialized
* cannot be reseated to refer to another object
* does not have the normal null state of a pointer
* is used like the original object

### Core distinction

```text
POINTER
    ↓
stores an address
    ↓
can be redirected

REFERENCE
    ↓
aliases an existing object
    ↓
cannot be reseated
```

---

# 13. Reference Cannot Be Reseated

Consider:

```cpp
int x = 10;
int y = 50;

int& r = x;
```

Now:

```cpp
r = y;
```

does **not** make `r` refer to `y`.

Instead it copies the value of `y` into the object `r` refers to:

```text
x = 50
y = 50
r still refers to x
```

A reference does not get redirected this way.

---

# 14. Why Does a Reference Need Initialization?

This is invalid:

```cpp
int& r;
```

A reference must immediately refer to an existing object.

Valid:

```cpp
int x = 10;
int& r = x;
```

Mental model:

```text
Reference
    ↓
Which object do you alias?
    ↓
Must be known when the reference is created
```

By contrast:

```cpp
int* p;
```

is a valid declaration because `p` is a pointer variable. It can later be assigned an address:

```cpp
p = &x;
```

However, an uninitialized pointer contains an indeterminate value and must not be dereferenced.

---

# 15. `nullptr`

Modern C++ uses:

```cpp
nullptr
```

to represent a pointer that currently points to nothing.

Example:

```cpp
int* p = nullptr;
```

This is valid.

You can test:

```cpp
if (p == nullptr) {
    cout << "p points to nothing";
}
```

The pointer itself is not an error.

---

# 16. Null Pointer vs Uninitialized Pointer

These are different.

### Uninitialized

```cpp
int* p;
```

`p` contains an indeterminate value.

It is unsafe to use it as though it points to an object.

### Null

```cpp
int* p = nullptr;
```

`p` is deliberately initialized to a known state:

> It points to nothing.

---

# 17. Dereferencing an Invalid Pointer

This is dangerous:

```cpp
int* p = nullptr;

cout << *p;
```

A null pointer cannot be dereferenced safely.

Similarly, this is dangerous:

```cpp
int* p;

cout << *p;
```

because `p` is uninitialized.

These situations lead to **undefined behavior**, not necessarily a guaranteed compilation error.

Undefined behavior means the C++ language gives no reliable result. The program may crash, produce unexpected output, appear to work, or behave differently under different circumstances.

### Safe pattern

```cpp
int x = 10;
int* p = &x;

if (p != nullptr) {
    cout << *p;
}
```

---

# 18. Stack vs Heap

The words "stack" and "heap" are sometimes confusing because **heap memory** is not the same thing as the **heap data structure**.

## Heap data structure

A heap data structure is something like a binary heap used in algorithms/priority queues.

It has properties such as:

* parent-child relationships
* heap-order property
* efficient access to the minimum/maximum element

That is NOT what we mean when discussing `new`.

---

## Heap memory

Heap memory refers to the area used for **dynamic memory allocation**.

Example:

```cpp
int* p = new int(20);
```

Conceptually:

```text
STACK                     HEAP

p ─────────────────────► [20]
```

`p` is the pointer variable.

`20` is the dynamically allocated integer.

The pointer and the object are separate entities.

---

# 19. Stack Memory

A local variable such as:

```cpp
void test() {
    int x = 10;
}
```

is typically associated with automatic/stack storage.

Its lifetime is tied to its scope.

When `test()` finishes, the local object `x`'s lifetime ends.

---

# 20. Heap Memory

Consider:

```cpp
int* p = new int(20);
```

`new int(20)`:

1. dynamically allocates memory for an `int`
2. initializes it to `20`
3. returns the address of that object

The address is stored in `p`.

Conceptually:

```text
STACK                     HEAP

p ─────────────────────► [20]
```

---

# 21. Why Use Dynamic/Heap Memory?

One major reason is that memory can be allocated **at runtime**.

For example:

```cpp
int n;
cin >> n;

int* arr = new int[n];
```

The program may not know `n` when it is compiled.

Dynamic allocation allows the program to request memory based on runtime requirements.

Another reason is that the dynamically allocated object's lifetime can extend beyond the scope of the pointer variable that originally created/accessed it.

---

# 22. `delete`

If memory was dynamically allocated with:

```cpp
new
```

manual allocation must traditionally be released with:

```cpp
delete
```

Example:

```cpp
int* p = new int(20);

cout << *p;

delete p;
```

After `delete`, the allocated object no longer exists.

The pointer variable `p` itself still exists if it is still in scope, but it is no longer safe to dereference as though it points to a valid object.

---

# 23. Dangling Pointer

A **dangling pointer** is a pointer that still contains an address, but the object at that address no longer exists or is no longer valid to access.

Example:

```cpp
int* p = nullptr;

{
    int x = 10;
    p = &x;
}

cout << *p;   // undefined behavior
```

Why?

Inside the block:

```text
p ─────► x
```

When the block ends:

```text
x's lifetime ends
```

But `p` still contains the old address.

Conceptually:

```text
p ─────► [object no longer exists]
```

Therefore dereferencing `p` is invalid.

---

# 24. Scope vs Lifetime

These are related but different concepts.

## Scope

> Where in the source code can I refer to an object by its name?

Example:

```cpp
{
    int x = 10;

    cout << x;  // valid
}

cout << x;      // invalid: x is out of scope
```

## Lifetime

> How long does the object actually exist?

For an ordinary local variable:

```cpp
{
    int x = 10;
}
```

`x`'s lifetime ends when it leaves its scope.

For a dynamically allocated object:

```cpp
int* p = new int(10);
```

the heap object can remain alive until:

```cpp
delete p;
```

or until the process terminates and the operating system reclaims the process's memory.

---

# 25. Scope of `{}`

Braces create a block/scope:

```cpp
{
    int x = 10;
}
```

The braces are meaningful.

They control the scope of variables with automatic storage duration.

For example:

```cpp
{
    int x = 10;
    cout << x;
}

// x is no longer accessible here
```

---

# 26. Pointer Variable vs Pointed-to Object

This is one of the most important concepts in memory.

Consider:

```cpp
int* x = new int(10);
```

There are two things:

```text
STACK                     HEAP

x ─────────────────────► [10]
↑                         ↑
pointer variable          dynamically allocated object
```

The variable `x` and the integer `10` are different objects.

The pointer variable can go out of scope while the heap object remains alive.

For example:

```cpp
int* getNumber() {
    int* p = new int(10);
    return p;
}
```

When the function returns:

```text
local pointer p disappears
heap integer 10 remains
returned address can still point to it
```

The caller can then eventually release the object:

```cpp
int* x = getNumber();

cout << *x;

delete x;
```

---

# 27. Memory and Program Lifetime

For a running program, its memory is managed by the operating system.

For interview-level understanding:

```text
Program starts
    ↓
OS provides process memory
    ↓
program uses stack/heap/etc.
    ↓
program exits
    ↓
OS reclaims the process's memory
```

However, this does NOT mean memory leaks are harmless.

If a program repeatedly allocates memory without releasing it:

```cpp
while (true) {
    int* p = new int(100);
}
```

it can consume more and more memory while it is running.

This is a **memory leak**.

The operating system eventually cleans up the process when it terminates, but that does not prevent problems during execution.

---

# 28. RAM / Virtual Memory Mental Model

For a simplified interview model, think of program memory as:

```text
Process Memory
├── Code
├── Global / static data
├── Heap      ← dynamic allocations
└── Stack     ← function/local automatic storage
```

Modern operating systems use **virtual memory**, so the exact physical relationship with RAM is more complicated than this simplified diagram.

For interview purposes, the important ideas are:

* memory belongs to the process while it runs
* stack and heap are different areas/uses of the process's memory
* local objects usually have scope-based automatic lifetime
* dynamic objects have explicitly managed lifetime (unless managed by higher-level C++ facilities)

---

# 29. Functions — Pass by Value

Consider:

```cpp
void change(int x) {
    x = 100;
}

int main() {
    int a = 10;

    change(a);

    cout << a;
}
```

Output:

```text
10
```

Why?

Because `x` is a **copy** of `a`.

Conceptually:

```text
main()                    change()

a = 10     ──copy──►     x = 10

                         x = 100
```

Changing `x` does not change `a`.

This is called:

* pass by value
* call by value

Both terms refer to the same idea.

---

# 30. Returning a Value

A pass-by-value function can still affect the caller if it returns a value and the caller assigns that value.

Example:

```cpp
int change(int x) {
    x = 100;
    return x;
}

int main() {
    int a = 10;

    a = change(a);

    cout << a;
}
```

Now:

```text
a = 10
  ↓
copy into x
  ↓
x = 100
  ↓
return 100
  ↓
a = 100
```

The original `a` was not directly modified by the function. The caller explicitly replaced its value with the returned value.

---

# 31. Pass by Reference

Example:

```cpp
void change(int& x) {
    x = 100;
}

int main() {
    int a = 10;

    change(a);

    cout << a;
}
```

Output:

```text
100
```

Why?

`x` is a reference to `a`.

Conceptually:

```text
a ─────┐
       ├── same object
x ─────┘
```

Therefore:

```cpp
x = 100;
```

changes `a`.

No copy of the integer is required.

---

# 32. Pass by Pointer

Example:

```cpp
void change(int* x) {
    *x = 100;
}

int main() {
    int a = 10;

    change(&a);

    cout << a;
}
```

The caller explicitly passes the address:

```cpp
change(&a);
```

Inside the function:

```cpp
*x = 100;
```

means:

> Go to the address stored in `x` and modify the value there.

Therefore `a` becomes `100`.

---

# 33. Value vs Reference vs Pointer

## Pass by value

```cpp
void f(int x)
```

```text
copy is made
original normally unchanged
```

## Pass by reference

```cpp
void f(int& x)
```

```text
x is an alias for the original object
original can be modified
```

## Pass by pointer

```cpp
void f(int* x)
```

Called with:

```cpp
f(&a);
```

```text
an address is passed
*x accesses the original object
```

---

# 34. Important Comparison

Suppose:

```cpp
int a = 10;
```

### Value

```cpp
void f(int x) {
    x++;
}

f(a);
```

Result:

```text
a = 10
```

### Reference

```cpp
void g(int& x) {
    x++;
}

g(a);
```

Result:

```text
a = 11
```

### Pointer

```cpp
void h(int* x) {
    (*x)++;
}

h(&a);
```

Result:

```text
a = 12
```

---

# 35. Pointer Increment vs Pointed-to Value Increment

Given:

```cpp
int a = 10;
int* p = &a;
```

These are different:

```cpp
p++;
```

and:

```cpp
(*p)++;
```

## `p++`

Changes the pointer itself.

It attempts to move the pointer to another location according to pointer arithmetic rules.

Pointer arithmetic is meaningful primarily when navigating elements of an array/object sequence.

## `(*p)++`

Dereferences the pointer first and increments the value it points to.

So:

```text
p++       → change the pointer
(*p)++    → change the pointed-to value
```

---

# 36. `const` Reference

Consider:

```cpp
void print(const string& s) {
    cout << s;
}
```

This means:

* pass by reference → no unnecessary copy
* `const` → function cannot modify the referenced string

Therefore this is invalid:

```cpp
void print(const string& s) {
    s += "hello";   // invalid
}
```

But this is fine:

```cpp
void print(const string& s) {
    cout << s;
}
```

---

# 37. Why `const&` Is Useful

Compare:

```cpp
void process(string s);
```

with:

```cpp
void process(const string& s);
```

The first generally creates a copy when the function is called.

The second:

* avoids copying
* allows read-only access
* can be much more efficient for large objects

This pattern becomes extremely common with STL containers:

```cpp
void process(const vector<int>& v);
```

It means:

> "Use the caller's vector without copying it, but don't modify it."

---

# 38. Important Interview Mental Models

Memorize these, not just the syntax.

### Pointer

```text
A pointer stores an address.
```

### Dereference

```text
*p means the value at the address stored in p.
```

### Reference

```text
A reference is an alias for an existing object.
```

### Pointer reassignment

```text
A pointer can be redirected.
```

### Reference assignment

```text
Assigning through a reference changes the object it refers to;
it does not reseat the reference.
```

### `nullptr`

```text
A valid pointer value meaning "points to nothing."
```

### Uninitialized pointer

```text
Contains an indeterminate value.
Do not dereference it.
```

### Dangling pointer

```text
Points to an object whose lifetime has ended
or whose storage is otherwise no longer valid.
```

### Pass by value

```text
The function receives a copy.
```

### Pass by reference

```text
The function receives an alias to the original object.
```

### Pass by pointer

```text
The function receives an address.
```

### `const&`

```text
No copy + cannot modify the referenced object.
```

---

# 39. Core Examples to Re-Type

These are worth actually typing and running.

## Example A — Pointer

```cpp
#include <iostream>
using namespace std;

int main() {
    int x = 10;

    int* p = &x;

    cout << x << "\n";
    cout << *p << "\n";

    *p = 20;

    cout << x << "\n";
}
```

Expected output:

```text
10
10
20
```

---

## Example B — Reference

```cpp
#include <iostream>
using namespace std;

int main() {
    int x = 10;

    int& r = x;

    r = 20;

    cout << x << "\n";
    cout << r << "\n";
}
```

Expected output:

```text
20
20
```

---

## Example C — Pointer and Reference Together

```cpp
#include <iostream>
using namespace std;

int main() {
    int x = 10;
    int y = 50;

    int* p = &x;
    int& r = x;

    *p = 20;
    r = 30;

    p = &y;
    *p = 40;

    cout << x << "\n";
    cout << y << "\n";
}
```

Expected output:

```text
30
40
```

Trace:

```text
Initial:
x = 10
y = 50
p → x
r → x

*p = 20
x = 20

r = 30
x = 30

p = &y
p → y

*p = 40
y = 40
```

Final:

```text
x = 30
y = 40
r refers to x
p points to y
```

---

## Example D — Pass by Value / Reference / Pointer

```cpp
#include <iostream>
using namespace std;

void f(int x) {
    x++;
}

void g(int& x) {
    x++;
}

void h(int* x) {
    (*x)++;
}

int main() {
    int a = 10;

    f(a);
    g(a);
    h(&a);

    cout << a;
}
```

Output:

```text
12
```

Trace:

```text
Initial a = 10

f(a)
a remains 10

g(a)
a becomes 11

h(&a)
a becomes 12
```

---

# 40. Common Interview Traps

### Trap 1

```cpp
int* p;
*p = 10;
```

Wrong because `p` is uninitialized.

---

### Trap 2

```cpp
int* p = nullptr;
*p = 10;
```

Wrong because `p` points to nothing.

---

### Trap 3

```cpp
int x = 10;
int& r = x;

int y = 20;
r = y;
```

`r` does NOT start referring to `y`.

Result:

```text
x = 20
y = 20
r still refers to x
```

---

### Trap 4

```cpp
int* p = &x;
p = &y;
```

This DOES redirect the pointer.

---

### Trap 5

```cpp
int* p = nullptr;

if (p != nullptr) {
    cout << *p;
}
```

Safe because dereferencing only happens if `p` points to something.

---

### Trap 6

```cpp
int* p;

{
    int x = 10;
    p = &x;
}

cout << *p;
```

Undefined behavior because `x`'s lifetime ended when the block ended.

---

# 41. Interview Quick-Answer Sheet

### What is a pointer?

A variable that stores the address of another object.

### What does `&x` mean?

The address of `x` (when used as the address-of operator).

### What does `*p` mean?

The value/object obtained by dereferencing pointer `p`.

### What is a reference?

An alias for an existing object.

### Pointer vs reference?

A pointer stores an address, can be null, and can be redirected. A reference aliases an existing object and cannot be reseated.

### What is `nullptr`?

A null pointer value representing "points to nothing."

### What is undefined behavior?

Behavior for which the C++ standard imposes no requirements; the program's result cannot be relied upon.

### What is a dangling pointer?

A pointer whose referenced object is no longer alive/valid.

### Stack vs heap?

The stack is typically used for automatic, scope-based storage. The heap is typically used for dynamically allocated storage whose lifetime can be controlled separately.

### Why use dynamic allocation?

For runtime-sized or dynamically managed objects/lifetimes.

### Why is `delete` needed?

To release memory obtained through manual dynamic allocation with `new`.

### Why use `const T&`?

To avoid copying an object while preventing the function from modifying it.

### Pass by value?

A copy is passed.

### Pass by reference?

An alias to the original object is passed.

### Pass by pointer?

An address is passed explicitly.

---

# 42. Chunk 1 + Chunk 2 Summary

The concepts form one connected chain:

```text
Variables
   ↓
Memory
   ↓
Addresses
   ↓
Pointers
   ↓
Dereferencing
   ↓
References
   ↓
nullptr / invalid pointers
   ↓
Stack / heap
   ↓
Object lifetime / scope
   ↓
Dangling pointers
   ↓
Functions
   ↓
Pass by value
   ↓
Pass by reference
   ↓
Pass by pointer
   ↓
const reference
```

The most important mental distinction is:

```text
POINTER
    stores an address

REFERENCE
    aliases an object

VALUE PARAMETER
    receives a copy

REFERENCE PARAMETER
    refers to the original

POINTER PARAMETER
    receives an address
```

Once these are clear, a large amount of C++ syntax becomes much easier to reason about rather than memorize.
