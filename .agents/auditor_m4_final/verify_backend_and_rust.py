import subprocess
import os
import re
import json

def verify_rust_engine():
    cargo_toml = r"c:\Users\juanc\Desktop\prueba\engine\genetic_optimizer\Cargo.toml"
    main_rs = r"c:\Users\juanc\Desktop\prueba\engine\genetic_optimizer\src\main.rs"
    
    with open(cargo_toml, "r", encoding="utf-8") as f:
        cargo = f.read()
    with open(main_rs, "r", encoding="utf-8") as f:
        rs_code = f.read()

    # Check for genuine GA implementation in Rust
    has_population = "struct Individual" in rs_code or "Individual" in rs_code
    has_crossover = "crossover" in rs_code or "mutate" in rs_code
    has_fitness = "fitness" in rs_code
    has_parallel = "rayon" in rs_code or "par_iter" in rs_code

    return {
        'cargo_exists': os.path.exists(cargo_toml),
        'main_rs_exists': os.path.exists(main_rs),
        'main_rs_len': len(rs_code),
        'has_population': has_population,
        'has_crossover': has_crossover,
        'has_fitness': has_fitness,
        'has_parallel': has_parallel
    }

def verify_app_routes_integrity():
    app_path = r"c:\Users\juanc\Desktop\prueba\app.py"
    with open(app_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Check routes
    routes = [
        "/api/data/pairs", "/api/data/candles", "/api/strategies",
        "/api/backtest", "/api/optimize", "/api/montecarlo",
        "/api/genetic/run", "/api/montecarlo-discrete", "/api/optimize-streak",
        "/api/smart-optimize", "/api/smart-optimize-v2", "/api/smart-optimize-v2-stream",
        "/api/backtest-stream", "/api/genetic/run-stream", "/api/smart-optimize-stream"
    ]

    missing_routes = [r for r in routes if r not in code]

    # Verify SSE streams yield real events (data: {...}\n\n)
    has_sse_generator = "yield f\"data:" in code or 'yield f"data:' in code
    has_rust_subprocess = "genetic_optimizer" in code and "subprocess" in code

    return {
        'missing_routes': missing_routes,
        'has_sse_generator': has_sse_generator,
        'has_rust_subprocess': has_rust_subprocess
    }

if __name__ == "__main__":
    rust_res = verify_rust_engine()
    routes_res = verify_app_routes_integrity()

    res = {
        'rust_engine': rust_res,
        'app_routes': routes_res
    }

    with open(r"c:\Users\juanc\Desktop\prueba\.agents\auditor_m4_final\backend_rust_audit.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print("Backend & Rust audit complete.")
