cmake_minimum_required(VERSION 2.8.12)
set(CMAKE_C_COMPILER "clang-3.8")
set(CMAKE_CXX_COMPILER "clang++-3.8")
project(pymplicit)
add_subdirectory(../../implisolid/lib/pybind11)


#find_package(Boost)
#include_directories(${Boost_INCLUDE_DIRS})
include_directories("/usr/include/boost/boost_1_61_0/")
include_directories("../../implisolid/lib/eigen")
#add_compile_options(-stdlib=libstdc++)
#add_compile_options(-lc++abi)

#add_compile_options(-std=c++14)

pybind11_add_module(pymplicit pyInterface.cpp)

