#include <string>
#include <filesystem>
#include <fstream>
#include <iostream>

namespace fs = std::filesystem;

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

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <filesystem>

namespace fs = std::filesystem;

bool get_max_energy_from_log(const fs::path &log, double &ret_energy)
{
    std::ifstream f(log.string());
    if (!f.is_open())
    {
        throw std::runtime_error("Could not open log file " + log.string());
    }

    std::string line;
    while (std::getline(f, line))
    {
        if (line.empty())
            continue;

        std::stringstream ss(line);
        std::string key;

        if (std::getline(ss, key, ':'))
        {
            auto first = key.find_first_not_of(" \t\r\n");
            auto last = key.find_last_not_of(" \t\r\n");

            if (first == std::string::npos)
                continue;
            std::string trimmed_key = key.substr(first, (last - first + 1));

            if (trimmed_key == "max_energy")
            {
                if (ss >> ret_energy)
                {
                    return true;
                }
            }
        }
    }
    return false;
}
