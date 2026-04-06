#include <iostream>
#include <filesystem>
#include <igl/readOBJ.h>
#include <igl/writeOBJ.h>
#include <igl/orientable_patches.h>
#include <igl/orient_outward.h>
#include <Eigen/Core>

namespace fs = std::filesystem;

/**
 * @param arg[0]
 * @param arg[1] path to input .obj file
 * @param arg[2] path to outut .obj file
 */
int main(int argc, char *argv[])
{
    // Basic argument check
    if (argc != 3)
    {
        std::cerr << "Usage: " << argv[0] << " <input_obj> <output_obj>" << std::endl;
        return 1;
    }

    // Assign arguments to variables
    std::string input_obj_fpath = argv[1];
    fs::path input_obj_path(input_obj_fpath);
    std::cout << "Processing meshes from: " << input_obj_fpath << std::endl;

    std::string output_obj_fpath = argv[2];
    fs::path output_obj_path(output_obj_fpath);
    std::cout << "Using curves from: " << output_obj_fpath << std::endl;

    Eigen::MatrixXd V;
    Eigen::MatrixXi F;
    Eigen::MatrixXi FF;

    if (!igl::readOBJ(input_obj_fpath, V, F))
    {
        std::cerr << "Failed to load " << input_obj_fpath << std::endl;
        return 1;
    }

    Eigen::VectorXi C;
    igl::orientable_patches(F, C);
    Eigen::VectorXi I;
    igl::orient_outward(V, F, C, FF, I);

    if (!igl::writeOBJ(output_obj_fpath, V, FF))
    {
        std::cerr << "Failed to save " << output_obj_fpath << std::endl;
        return 1;
    }
    std::cout << "Succesfully reoriented and saved to " << output_obj_fpath << std::endl;
}