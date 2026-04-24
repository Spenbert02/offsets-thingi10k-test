#include <iostream>
#include <filesystem>
#include <fstream>
#include <string>
#include <map>
#include <set>
#include "utils.hpp"
#include <stdexcept>

namespace fs = std::filesystem;

const int NOLOG = 0;
const int LOG_BADENERGY = 1;
const int SUCCESS = 2;

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        std::cerr << "Usage: " << argv[0] << "/path/to/model/directory" << std::endl;
        return 1;
    }

    std::string models_dir_str = argv[1];
    fs::path models_dir_path(models_dir_str);
    if (!fs::is_directory(models_dir_path))
    {
        std::cerr << "Model directory " << models_dir_path << " does not exist." << std::endl;
        return 1;
    }
    else
    {
        std::cout << "Using models directory " << models_dir_path << std::endl;
    }

    // track: empty input, inverted element in input, timeout, completed, other
    std::map<int, int> outcomes;

    int processed_count = 0;
    for (const auto &entry : fs::directory_iterator(models_dir_path))
    {
        if (!entry.is_directory())
        {
            continue;
        }
        int model_id;
        if (!get_model_id(entry.path().filename(), model_id))
        {
            std::cout << std::endl
                      << "WARNING: non-int-parseable subdir " << entry.path() << std::endl;
            continue;
        }

        fs::path log_path(entry.path() / "remeshing_test2" / ("model_" + std::to_string(model_id) + "_out.log"));
        if (!fs::exists(log_path))
        {
            outcomes[model_id] = NOLOG;
            continue;
        }

        double max_energy;
        if (get_max_energy_from_log(log_path, max_energy))
        {
            if (max_energy < 100.0)
            {
                outcomes[model_id] = SUCCESS;
            }
            else
            {
                outcomes[model_id] = LOG_BADENERGY;
            }
        }
        else
        {
            outcomes[model_id] = LOG_BADENERGY;
        }
    }

    std::map<int, int> counts;
    counts[SUCCESS] = 0;
    counts[NOLOG] = 0;
    counts[LOG_BADENERGY] = 0;
    for (const auto &pair : outcomes)
    {
        counts[pair.second] += 1;
    }

    // print findings
    std::cout << "========== REMESHING TEST 2 FINDINGS ==========" << std::endl;
    std::cout << "successes: " << counts[SUCCESS] << std::endl;
    std::cout << "no log file: " << counts[NOLOG] << std::endl;
    std::cout << "bad energy: " << counts[LOG_BADENERGY] << std::endl;
    for (const auto &pair : outcomes)
    {
        if (pair.second == LOG_BADENERGY)
        {
            std::cout << "\tmodel id " << pair.first << std::endl;
        }
    }
}
