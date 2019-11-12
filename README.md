# Corappo

*A tool to automatically generate CMakeLists.txt*

Often times, especially when working on things like school assignments,
simple projects are provided with a simple Makefile. However, IDEs
like [juCi++](https://gitlab.com/cppit/jucipp) and [CLion](https://www.jetbrains.com/clion/)
only autoload from projects that build with CMake. This tool attempts
to generate a CMakeLists.txt from the build output of another build system.
This assumes that the other build system writes compiler commands to stdout.

## Usage

```bash
make clean  # Make sure you're doing a full build
make | corappo | tee CMakeLists.txt
```

Corappo reads build output from stdin and writes the corresponding CMakeLists.txt to stdout.

## Installation

```bash
pip3 install --user corappo
```

## Example

Here's an example of it in action.

**Makefile output:**

```bash
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o simplecache_main.o simplecache_main.cpp
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o simplecache.o simplecache.cpp
clang++  -o simplecache simplecache_main.o simplecache.o
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o cache.o cache.cpp
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o cacheblock.o cacheblock.cpp
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o cacheconfig.o cacheconfig.cpp
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o cachesimulator.o cachesimulator.cpp
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o main.o main.cpp
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o utils.o utils.cpp
clang++  -o cachesim cache.o cacheblock.o cacheconfig.o cachesimulator.o main.o utils.o
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o cacheblock_test.o cacheblock_test.cpp
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o cacheconfig_test.o cacheconfig_test.cpp
clang++ -g -Wall -Werror -Wno-unused-parameter -Wno-unused-private-field -std=c++11 -isystem gtest-1.8.0/include  -c -o utils_test.o utils_test.cpp
clang++  -pthread -o unit_tests cacheblock.o cacheblock_test.o cacheconfig.o cacheconfig_test.o utils.o utils_test.o gtest-1.8.0/make/gtest_main.a
```

**Generated CMakeLists.txt:**

```cmake
cmake_minimum_required(VERSION 2.8)

project(simplecache)

set(CMAKE_CXX_STANDARD 11)

find_package(Threads)

include_directories(gtest-1.8.0/include)

add_executable(
    simplecache
    simplecache_main.cpp
    simplecache.cpp
)

add_executable(
    cachesim
    cache.cpp
    cacheblock.cpp
    cacheconfig.cpp
    cachesimulator.cpp
    main.cpp
    utils.cpp
)

add_executable(
    unit_tests
    cacheblock.cpp
    cacheblock_test.cpp
    cacheconfig.cpp
    cacheconfig_test.cpp
    utils.cpp
    utils_test.cpp
)

target_link_libraries(
    unit_tests
    ${CMAKE_CURRENT_LIST_DIR}/gtest-1.8.0/make/gtest_main.a
    ${CMAKE_THREAD_LIBS_INIT}
)
```
