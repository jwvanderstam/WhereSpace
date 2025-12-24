#!/bin/bash
# JW zijn babbeldoos - Quick Start Script
# ========================================

echo ""
echo "============================================================"
echo "   JW zijn babbeldoos - AI Document Chat System"
echo "============================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python niet gevonden!"
    echo "Installeer Python van: https://www.python.org/downloads/"
    exit 1
fi

echo "Python gevonden!"
echo ""

# Check dependencies
echo "Controleren op vereisten..."

# Voer het afhankelijkheid controle script uit
python3 check_dependencies.py
# Controleer de exit status van het vorige commando
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Controle van afhankelijkheden mislukt!"
    echo "Installeer ontbrekende pakketten handmatig."
    echo ""
    exit 1
fi

echo ""
echo "Afhankelijkheden OK!"
echo ""

# Start hoofdmenu
python3 main.py
