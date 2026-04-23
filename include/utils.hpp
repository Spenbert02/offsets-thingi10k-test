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

bool get_max_energy_from_log(const fs::path &log, double &ret_energy)
{
    std::ifstream f(log.string());
    if (!f.is_open())
    {
        std::string errstr = "Could not open log file " + log.string();
        throw std::runtime_error(errstr);
    }

    std::string line;
    while (std::getline(f, line))
    {
        if (line.empty())
            continue;
        size_t colon_pos = line.find(":");
        if (colon_pos == std::string::npos)
            continue;
        std::string key = line.substr(0, colon_pos);
        key.erase(std::remove_if(key.begin(), key.end(), ::isspace), key.end());
        if (key == "max_energy")
        {
            std::string value_str = line.substr(colon_pos + 1);
            try
            {
                ret_energy = std::stod(value_str);
                return true;
            }
            catch (const std::exception &e)
            {
                continue;
            }
        }
    }
    return false;
}
