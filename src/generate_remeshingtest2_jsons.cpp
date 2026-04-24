#include <string>
#include <filesystem>
#include <nlohmann/json.hpp>
#include <fstream>
#include "utils.hpp"
#include <iostream>

namespace fs = std::filesystem;
using json = nlohmann::json;

/**
 * @brief usage: ./generate_remeshingtest2_jsons <model_dir>
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

        // create remeshing_test2 dir and json file
        fs::path remeshing_test2_dir(entry.path() / "remeshing_test2");
        fs::create_directory(remeshing_test2_dir);
        json j;
        j["application"] = "image_simulation";
        json input_array = json::array();
        input_array.push_back(oriented_obj_path.string());
        j["input"] = input_array;
        j["eps_rel"] = 1e-2;
        j["w_amips"] = 1e-4;
        j["stop_energy"] = 100;
        j["smooth_without_envelope"] = false;
        j["num_threads"] = 12;
        j["write_vtu"] = true;
        j["debug_output"] = false;
        j["output"] = "model_" + std::to_string(model_id) + "_out";

        fs::path json_path(remeshing_test2_dir / ("remeshing_test2_" + std::to_string(model_id) + ".json"));
        std::ofstream out(json_path.string());
        out << j.dump(4) << std::endl;

        if ((++created_count) % 100 == 0)
        {
            std::cout << "\r" << created_count << "\t" << std::flush;
        }
    }
    std::cout << std::endl
              << "created " << created_count << " jsons" << std::endl;
}
