cmake_minimum_required(VERSION 3.10)

# 项目配置
project(Dickson-Engine VERSION 1.0.0 LANGUAGES C CXX)

# 标准设置
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# --- 1. 核心库 (Dickson Core, Pure C) ---
include_directories(core/include)
file(GLOB CORE_SOURCES "core/src/dickson.c" "core/src/poly_alg.c" "core/src/primes_seeds.c")
add_library(dickson_core STATIC ${CORE_SOURCES})

# --- 2. 命令行工具 (CLI) ---
add_executable(dickson_cli core/src/main.c)
target_link_libraries(dickson_cli dickson_core)

# --- 3. NTL Benchmark (C++) ---

# 在 Linux 下，find_path/find_library 默认会去 /usr/include 和 /usr/lib 找
# 所以我们不需要那些 HINTS 了
find_path(NTL_INCLUDE_DIR NAMES NTL/ZZ.h)
find_library(NTL_LIB NAMES ntl)
find_library(GMP_LIB NAMES gmp)

if(NTL_INCLUDE_DIR AND NTL_LIB)
    message(STATUS "Found NTL: ${NTL_LIB}")
    
    add_executable(ntl_bench benchmark/ntl_bench.cpp)
    
    # 依然保留 SYSTEM，这是一个好习惯，压制第三方库的警告
    target_include_directories(ntl_bench SYSTEM PRIVATE ${NTL_INCLUDE_DIR})
    
    # 链接库 (如果有 GMP 就一起链接，这是 NTL 的标准操作)
    if(GMP_LIB)
        target_link_libraries(ntl_bench ${NTL_LIB} ${GMP_LIB})
    else()
        target_link_libraries(ntl_bench ${NTL_LIB})
    endif()
    
else()
    message(WARNING "NTL library not found! Benchmark target 'ntl_bench' will not be built.")
    message(WARNING "Ubuntu users: sudo apt-get install libntl-dev")
endif()

# --- [NEW] 4. Dickson Benchmark ---
add_executable(dickson_bench benchmark/dickson_bench.c)
target_link_libraries(dickson_bench dickson_core)

# --- [NEW] 5. Oxygen Tank Generator ---
add_executable(oxy_tank benchmark/oxygen_tank_generator.c)
target_link_libraries(oxy_tank dickson_core)
