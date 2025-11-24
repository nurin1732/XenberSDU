{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyPURy0TunPVJsAcuiJamZQC"
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "poQW1CIr2qE1"
      },
      "outputs": [],
      "source": [
        "# Frontend (Streamlit) — Intelligent Predictive Analytics\n",
        "\n",
        "## What this provides\n",
        "- Multi-tab dashboard: Home, Forecasting, Anomaly Detection, Optimization, Alerts.\n",
        "- Auto-refresh with configurable interval.\n",
        "- Works with backend API, and gracefully falls back to mock data.\n",
        "- Download buttons for CSV/JSON exports.\n",
        "- Clean, judge-friendly layout.\n",
        "\n",
        "## Prerequisites\n",
        "- Python 3.9+ recommended\n",
        "- Requirements installed at repo root\n",
        "\n",
        "## Run\n",
        "```bash\n",
        "# From repo root, after installing requirements\n",
        "export API_BASE_URL=\"http://localhost:8000\"  # adjust if deployed\n",
        "export REFRESH_MS=5000\n",
        "streamlit run frontend/dashboard.py"
      ]
    }
  ]
}