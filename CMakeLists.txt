cmake_minimum_required(VERSION 3.10)
project(OrientNormals)

# Use C++17 for modern filesystem support (great for directory iteration)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# dependencies
set(EIGEN3_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/external/eigen")
add_subdirectory(external/eigen)
add_subdirectory(external/libigl)
add_subdirectory(external/MshIO)
add_subdirectory(external/json EXCLUDE_FROM_ALL)

# EXECUTABLES
add_executable(orient_obj src/orient_normals.cpp)
target_link_libraries(orient_obj PRIVATE igl::core Eigen3::Eigen)
target_include_directories(orient_obj PRIVATE include)

add_executable(check_completed src/check_completed.cpp)

add_executable(manifold_check_completed src/manifold_check_completed.cpp)

add_executable(generate_remeshingtest1_jsons src/generate_remeshingtest1_jsons.cpp)
target_link_libraries(generate_remeshingtest1_jsons PRIVATE mshio::mshio Eigen3::Eigen igl::core nlohmann_json::nlohmann_json)
target_include_directories(generate_remeshingtest1_jsons PRIVATE include)

add_executable(generate_remeshingtest2_jsons src/generate_remeshingtest2_jsons.cpp)
target_link_libraries(generate_remeshingtest2_jsons PRIVATE nlohmann_json::nlohmann_json)
target_include_directories(generate_remeshingtest2_jsons PRIVATE include)

add_executable(check_remeshing_test1_completed src/check_remeshing_test1_completed.cpp)
target_include_directories(check_remeshing_test1_completed PRIVATE include)

# Optimization: Ensure we build in Release mode by default for speed
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()