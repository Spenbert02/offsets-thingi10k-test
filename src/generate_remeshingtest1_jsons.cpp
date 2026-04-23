#include "msh_help.hpp"
#include <string>
#include <filesystem>
#include <igl/read_triangle_mesh.h>
#include <Eigen/Core>
#include <nlohmann/json.hpp>
#include <fstream>

namespace fs = std::filesystem;
using namespace Eigen;
using json = nlohmann::json;

bool get_model_id(const std::string &name, int &id)
{
    std::size_t start = name.find("model_");
    if (start == std::string::npos)
    {
        return false;
    }

    start += 6;
    std::size_t end = start;
    while (end < name.size() && std::isdigit(static_cast<unsigned char>(name[end])))
    {
        ++end;
    }
    if (start == end)
    {
        return false;
    }
    id = std::stoi(name.substr(start, end - start));
    return true;
}

/**
 * @brief usage: ./generate_remeshingtest1_jsons <model_dir>
 */
int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        std::cerr << "Usage: " << argv[0] << " /path/to/models/directory" << std::endl;
        return 1;
    }

    std::string model_dir_str = argv[1];
    fs::path model_dir_path(model_dir_str);
    if (!fs::is_directory(model_dir_path))
    {
        std::cerr << "Model directory " << model_dir_path << " does not exist" << std::endl;
        return 1;
    }

    int created_count = 0;
    std::cout << "\r" << created_count;
    for (const auto &entry : fs::directory_iterator(model_dir_path))
    {
        if (!entry.is_directory())
        {
            continue;
        }

        // extract model id from directory name
        std::string dirname = entry.path().filename();
        int model_id;
        if (!get_model_id(dirname, model_id))
        {
            std::cout << std::endl
                      << "WARNING: non-int-parseable subdir " << entry.path() << std::endl;
            continue;
        }

        // make oriented obj path
        fs::path oriented_obj_path(entry.path() / "orient_output" / ("model_" + std::to_string(model_id) + "_oriented.obj"));
        if (!fs::exists(oriented_obj_path))
        {
            std::cout << std::endl
                      << "WARNING: no oriented obj for model " << model_id << std::endl;
            continue;
        }

        // read .obj, get bounding box size
        MatrixXd V;
        MatrixXi F;
        igl::read_triangle_mesh(oriented_obj_path.string(), V, F);

        VectorXd mins = V.colwise().minCoeff();
        VectorXd maxes = V.colwise().maxCoeff();
        double diag_l = (maxes - mins).norm();
        double offset = 0.15 * diag_l;

        // create remeshing_test1 dir and json file
        fs::path remeshing_test1_dir(entry.path() / "remeshing_test1");
        fs::create_directory(remeshing_test1_dir);
        json j;
        j["application"] = "image_simulation";
        json input_array = json::array();
        for (int i = 0; i < 2; i++)
        {
            input_array.push_back(oriented_obj_path.string());
        }
        j["input"] = input_array;
        std::vector<std::vector<double>> matrix = {{{{1.0, 0.0, 0.0, offset}},
                                                    {{0.0, 1.0, 0.0, 0.0}},
                                                    {{0.0, 0.0, 1.0, 0.0}},
                                                    {{0.0, 0.0, 0.0, 1.0}}}};
        json transform_list = json::array();
        transform_list.push_back(json::array());
        transform_list.push_back(matrix);
        j["input_transform"] = transform_list;
        j["eps_rel"] = 1e-2;
        j["w_ampis"] = 1e-4;
        j["stop_energy"] = 10;
        j["smooth_without_envelope"] = false;
        j["num_threads"] = 0;
        j["write_vtu"] = true;
        j["debug_output"] = false;
        j["output"] = "model_" + std::to_string(model_id) + "_out";

        fs::path json_path(remeshing_test1_dir / ("remeshing_test1_" + std::to_string(model_id) + ".json"));
        std::ofstream out(json_path.string());
        out << j.dump(4) << std::endl;

        if ((++created_count) % 100 == 0)
        {
            std::cout << "\r" << created_count << "\t";
        }
    }
    std::cout << std::endl
              << "created " << created_count << " jsons" << std::endl;
}
