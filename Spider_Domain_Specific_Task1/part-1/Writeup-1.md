# Part 1 – Introduction to Fuzzing

## Objective

The objective of Part 1 was to understand the basic principles of fuzzing and how fuzzers are used to discover bugs and vulnerabilities in software.

Before starting this task, I had very little practical experience with fuzzing. I was aware that fuzzers generated random inputs and attempted to crash programs, but I did not understand how modern fuzzers operate internally or how they systematically explore software behavior.

This section served as a foundation for the later practical tasks involving AFL++ and harness development.

---

## What is Fuzzing?

Fuzzing is an automated software testing technique that repeatedly executes a program using large numbers of generated inputs.

The goal is to trigger unexpected behavior such as:

* Crashes
* Memory corruption
* Out-of-bounds accesses
* Use-after-free bugs
* Logic errors
* Unhandled exceptions

Instead of manually creating test cases, a fuzzer continuously generates or mutates inputs and observes how the target program behaves.

If an input causes the program to crash or behave unexpectedly, that input is saved for further analysis.

---

## Types of Fuzzers

During this task I learned that fuzzers can be categorized in several ways.

### Black-Box Fuzzers

Black-box fuzzers have no knowledge of the program's internal structure.

They generate inputs and observe outputs without examining source code or execution paths.

These fuzzers are simple but often inefficient because they have no guidance regarding which inputs are interesting.

---

### White-Box Fuzzers

White-box fuzzers have access to the internal structure of the program and may use techniques such as symbolic execution to systematically explore execution paths.

These fuzzers can achieve deeper exploration but are typically computationally expensive.

---

### Grey-Box Fuzzers

Grey-box fuzzers, such as AFL++, combine the advantages of both approaches.

They use lightweight instrumentation to measure code coverage while remaining fast enough to execute thousands of inputs per second.

This allows them to intelligently prioritize inputs that reach new areas of code.

---

## Coverage-Guided Fuzzing

One of the most important concepts I learned was coverage-guided fuzzing.

Initially, I assumed that fuzzers simply generated random data indefinitely.

I later learned that AFL++ operates very differently.

The general workflow is:

1. Execute an input
2. Measure which code paths were reached
3. Save inputs that discover new coverage
4. Mutate those successful inputs
5. Repeat the process continuously

This feedback loop allows AFL++ to progressively explore deeper execution paths rather than relying solely on random chance.

---

## Why Coverage Matters

Coverage is a measure of how much of a program has been executed.

A fuzzer that repeatedly exercises the same code path provides little value.

A fuzzer that continuously discovers new branches, conditions, and execution paths is much more effective.

During later stages of the project, I learned that coverage growth is often a more useful metric than crash count because coverage indicates whether the fuzzer is successfully exploring the target.

---

## Mutation Strategies

Another concept introduced during this task was mutation-based fuzzing.

Instead of generating completely random files, AFL++ modifies existing inputs using mutation strategies such as:

* Bit flips
* Byte flips
* Arithmetic mutations
* Block insertion and deletion
* Havoc mutations
* Splicing multiple inputs together

These techniques allow AFL++ to gradually transform valid inputs into new inputs that exercise different program behaviors.

---

## Importance of Seed Inputs

A fuzzing campaign typically begins with a set of initial inputs known as a seed corpus.

The quality of the seed corpus has a significant impact on fuzzing effectiveness.

Good seeds allow the fuzzer to immediately reach meaningful functionality.

Poor seeds may cause the target application to reject inputs before deeper logic can be explored.

This concept became particularly important during Part 2 when investigating why AFL++ struggled to progress through the license parser.

---

## Real-World Applications of Fuzzing

Fuzzing is widely used in industry to improve software reliability and security.

Common targets include:

* File format parsers
* Image processing libraries
* Browsers
* Operating system kernels
* Network protocol implementations
* Compression libraries
* Cryptographic software

Many critical security vulnerabilities have been discovered through fuzzing campaigns.

---

## Lessons Learned from Part 1

Part 1 provided the theoretical foundation necessary for the remainder of the project.

The most important concepts I learned were:

* The purpose of fuzzing
* The difference between black-box, white-box, and grey-box fuzzing
* How coverage-guided fuzzing works
* Why seed inputs matter
* How mutation strategies operate
* Why coverage is a better indicator of progress than crash count

These concepts became significantly clearer during Parts 2 and 3 when applying them in practice using AFL++.

