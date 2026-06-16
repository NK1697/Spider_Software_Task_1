# Spider Task 1 (2026) – Fuzzing Report

# Introduction

The objective of this task was to understand the fundamentals of coverage-guided fuzzing, repair a broken AFL++ harness, and gain practical experience using AFL++ to explore software behavior.

Prior to this project, my understanding of fuzzing was limited to the idea that a fuzzer generates random inputs in an attempt to crash a program. Through this task, I learned how modern fuzzers actually operate, how code coverage is used to guide mutations, why harnesses are required, and what challenges arise when fuzzing structured input formats.

---

# Part 2 – Harness Repair

## Project Overview

The provided software consisted of several components:

* `license.c` – Main license validation logic
* `license.h` – Interface definitions and declarations
* `afl_harness.c` – AFL++ harness provided with the assignment
* `test_license.c` – Unit testing program
* `Makefile` – Build configuration
* `corpus/` – Initial seed inputs

The goal was to identify flaws in the provided harness and repair it so AFL++ could effectively fuzz the target.

# Initial Investigation

My first step was understanding how the provided harness interacted with the target application.

Initially, AFL++ launched successfully and the target executed without crashing, which led me to believe that the harness was functioning correctly.

However, AFL++ showed little progress over time and coverage growth appeared minimal. This indicated that although execution was occurring, the fuzzer was not effectively exploring the target application.

# Understanding the Role of a Harness

One of the most important concepts I learned was the purpose of a fuzzing harness.

A harness serves as the bridge between AFL++ and the target software. It is responsible for:

* Reading AFL-generated inputs
* Passing those inputs into the target code
* Initializing required resources
* Cleaning up resources after execution
* Ensuring each execution is isolated and repeatable

Without a properly designed harness, AFL++ may run successfully while making little or no actual progress.

# Issues Found in the Original Harness

After reviewing `afl_harness.c`, I identified several issues.

### Missing Cleanup

The harness initialized the license system but never cleaned it up before exiting. This could leave internal state in an inconsistent condition between executions.

### Empty Input Handling

The harness processed inputs regardless of whether any meaningful data had been read from the file.

This caused unnecessary executions and provided no useful information to AFL++.

### Lack of Defensive Validation

The harness performed minimal validation of input conditions before passing data to the parser.

# Harness Fixes

The repaired harness introduced:

* Proper handling of empty inputs
* Cleanup of the license system after validation
* Improved execution stability
* Better compatibility with AFL++ workflows

These modifications ensured that each AFL execution began and ended in a predictable state.

# Major Debugging Challenges

## Verifying Recompilation

One of the most time-consuming issues I encountered was determining whether AFL++ was actually using my modified version of `license.c`.

Even after making changes, runtime behavior appeared unchanged.

To investigate, I repeatedly:

* Cleaned the build directory
* Recompiled all binaries
* Checked timestamps on generated object files
* Verified instrumentation messages during compilation

Eventually I confirmed that the modified source file was being compiled correctly and that the observed behavior was caused by parser logic rather than build system problems.


# Investigating Parser Validation

While examining `license.c`, I discovered that the parser performs multiple validation steps before reaching deeper functionality.

These included:

* CRC verification
* Version validation
* Chunk parsing
* Bounds checking
* Signature verification

Many AFL-generated inputs failed during these early checks.

As a result, AFL repeatedly exercised the same shallow execution paths.

This initially gave the impression that AFL++ was not working correctly, when in reality the parser was rejecting most generated inputs before deeper code could be reached.

# Seed Corpus Investigation

Due to the seed corpus containing a python script but the parser expecting a binary file of inputs, the provided seed immediately failed...

This discovery helped explain why AFL++ was struggling to reach meaningful portions of the codebase.

# Learning to Interpret AFL++

A significant portion of the project involved learning how AFL++ reports progress.

Initially I focused almost entirely on crashes.

Later I learned that coverage growth is a far more important indicator.

Key AFL concepts I learned include:

### Queue

Files stored in:

`findings/default/queue/`

represent inputs that discovered new execution paths.

Queue growth indicates that AFL++ is successfully exploring new code.

### Coverage

Coverage reflects how many unique branches or execution paths have been reached.

Increasing coverage is often more valuable than immediately finding crashes.

### Instrumentation

The messages produced during compilation showed how many locations AFL++ instrumented inside the target.

This provided confirmation that coverage tracking was functioning correctly.

# AFL++ Concepts Learned

## Coverage-Guided Fuzzing

Before this project, I believed fuzzing primarily relied on random input generation.

I learned that AFL++ uses a feedback loop:

1. Execute an input
2. Measure code coverage
3. Preserve inputs that discover new paths
4. Mutate those inputs further

This allows AFL++ to systematically explore increasingly complex execution paths.


## Mutation Strategies

I learned about AFL++ mutation stages, including:

### Bit and Byte Flips

Small modifications to individual bits and bytes.

### Arithmetic Mutations

Incrementing or decrementing values to discover boundary conditions.

### Havoc

Large collections of random mutations applied to promising inputs.

### Splice

Combining sections from multiple successful inputs to generate new test cases.

These mutation strategies allow AFL++ to explore far beyond what purely random generation would achieve.

## Structured Input Formats

The license parser demonstrated an important fuzzing challenge.

Structured formats often contain:

* Checksums
* Length fields
* Headers
* Signatures
* Version information

Random mutations frequently break these structures, causing execution to terminate before deeper functionality is reached.

This highlighted the importance of high-quality seed inputs and well-designed harnesses.
