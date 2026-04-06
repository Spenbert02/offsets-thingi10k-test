cmake_minimum_required(VERSION 3.10)
project(OrientNormals)

# Use C++17 for modern filesystem support (great for directory iteration)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# dependencies
set(EIGEN3_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/external/eigen")
add_subdirectory(external/eigen)
add_subdirectory(external/libigl)

# Define the executable and its source files
add_executable(orient_obj src/orient_normals.cpp)
target_link_libraries(orient_obj PRIVATE igl::core Eigen3::Eigen)
target_include_directories(orient_obj PRIVATE include)

# Optimization: Ensure we build in Release mode by default for speed
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()