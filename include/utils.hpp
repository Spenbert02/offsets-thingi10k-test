#include <string>

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
