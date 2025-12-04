cmake_minimum_required(VERSION 3.10)
project(Dickson-Engine VERSION 1.0.0)

set(CMAKE_C_STANDARD 99)

# 包含头文件目录
include_directories(core/include)

# 核心库
add_library(dickson_core core/src/dickson.c)

# CLI 可执行文件
add_executable(dickson_cli core/src/main.c)
target_link_libraries(dickson_cli dickson_core)

# TODO: Add NTL comparison target later
