#include <iostream>
#include "ABS.h"

int main() {
    // Esempio di utilizzo
    ABS myABS;
    auto result = myABS.get_info(15);

    // Visualizza le informazioni
    for (const auto& [key, value] : result) {
        std::cout << key << ": " << value << std::endl;
    }

    return 0;
}
