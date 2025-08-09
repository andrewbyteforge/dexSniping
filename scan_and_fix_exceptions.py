#!/usr/bin/env python3
"""
Scan and Fix All Exception References
File: scan_and_fix_exceptions.py

Scan all Python files to find referenced exceptions and add them to exceptions.py
"""

import re
from pathlib import Path
from typing import Set, List, Tuple


def scan_for_exception_imports() -> Set[str]:
    """Scan all Python files for exception imports."""
    
    exception_imports = set()
    
    # Python files to scan
    python_files = []
    
    # Scan app directory
    app_dir = Path("app")
    if app_dir.exists():
        python_files.extend(app_dir.rglob("*.py"))
    
    # Scan tests directory
    tests_dir = Path("tests")
    if tests_dir.exists():
        python_files.extend(tests_dir.rglob("*.py"))
    
    # Scan root directory
    python_files.extend(Path(".").glob("*.py"))
    
    print(f"Scanning {len(python_files)} Python files...")
    
    for py_file in python_files:
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # Find imports from app.core.exceptions
            patterns = [
                r'from app\.core\.exceptions import ([^#\n]+)',
                r'from \.\.exceptions import ([^#\n]+)',
                r'from \.exceptions import ([^#\n]+)',
                r'from exceptions import ([^#\n]+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Split by comma and clean up
                    imports = [imp.strip() for imp in match.split(',')]
                    for imp in imports:
                        # Remove parentheses, newlines, and extra whitespace
                        clean_imp = re.sub(r'[(),\n\r]', '', imp).strip()
                        if clean_imp and not clean_imp.startswith('#'):
                            exception_imports.add(clean_imp)
            
            # Also look for direct exception usage (raise SomeError)
            raise_pattern = r'raise (\w+Error)\b'
            raise_matches = re.findall(raise_pattern, content)
            for match in raise_matches:
                exception_imports.add(match)
                
        except Exception as e:
            print(f"⚠️ Could not scan {py_file}: {e}")
    
    return exception_imports


def get_existing_exceptions() -> Set[str]:
    """Get existing exceptions from exceptions.py"""
    
    exceptions_file = Path("app/core/exceptions.py")
    existing = set()
    
    if exceptions_file.exists():
        try:
            content = exceptions_file.read_text(encoding='utf-8')
            
            # Find all class definitions that look like exceptions
            class_pattern = r'class (\w+(?:Error|Exception))\b'
            matches = re.findall(class_pattern, content)
            for match in matches:
                existing.add(match)
                
        except Exception as e:
            print(f"⚠️ Could not read exceptions.py: {e}")
    
    return existing


def generate_missing_exceptions(referenced: Set[str], existing: Set[str]) -> List[Tuple[str, str, str]]:
    """Generate list of missing exceptions with appropriate parent classes."""
    
    missing = referenced - existing
    exception_definitions = []
    
    # Map exception names to appropriate parent classes
    parent_mapping = {
        # AI/ML exceptions
        'DataPreparationError': ('DataError', 'Data preparation errors.'),
        'ModelError': ('AIAnalysisError', 'Machine learning model errors.'),
        'ModelLoadError': ('AIAnalysisError', 'Model loading errors.'),
        'ModelTrainingError': ('AIAnalysisError', 'Model training errors.'),
        'ModelValidationError': ('AIAnalysisError', 'Model validation errors.'),
        'FeatureError': ('AIAnalysisError', 'Feature engineering errors.'),
        'PredictionError': ('AIAnalysisError', 'Prediction errors.'),
        'ClassificationError': ('AIAnalysisError', 'Classification errors.'),
        'RegressionError': ('AIAnalysisError', 'Regression errors.'),
        'ClusteringError': ('AIAnalysisError', 'Clustering errors.'),
        
        # Contract/Analysis exceptions
        'ContractAnalysisError': ('ContractError', 'Smart contract analysis errors.'),
        'ContractCompilationError': ('ContractError', 'Contract compilation errors.'),
        'ContractDeploymentError': ('ContractError', 'Contract deployment errors.'),
        'ContractInteractionError': ('ContractError', 'Contract interaction errors.'),
        'AbiError': ('ContractError', 'ABI parsing errors.'),
        'BytecodeError': ('ContractError', 'Bytecode analysis errors.'),
        
        # Token/Trading exceptions
        'TokenAnalysisError': ('AIAnalysisError', 'Token analysis errors.'),
        'TokenValidationError': ('ValidationError', 'Token validation errors.'),
        'TokenMetadataError': ('DataError', 'Token metadata errors.'),
        'PriceAnalysisError': ('DataAnalysisError', 'Price analysis errors.'),
        'VolumeAnalysisError': ('DataAnalysisError', 'Volume analysis errors.'),
        'LiquidityAnalysisError': ('DataAnalysisError', 'Liquidity analysis errors.'),
        
        # Data processing exceptions
        'DataAnalysisError': ('DataError', 'Data analysis errors.'),
        'DataProcessingError': ('DataError', 'Data processing errors.'),
        'DataValidationError': ('ValidationError', 'Data validation errors.'),
        'DataCleaningError': ('DataError', 'Data cleaning errors.'),
        'DataTransformationError': ('DataError', 'Data transformation errors.'),
        'DataNormalizationError': ('DataError', 'Data normalization errors.'),
        'DataAggregationError': ('DataError', 'Data aggregation errors.'),
        
        # Market/Financial exceptions
        'MarketAnalysisError': ('DataAnalysisError', 'Market analysis errors.'),
        'TechnicalAnalysisError': ('DataAnalysisError', 'Technical analysis errors.'),
        'FundamentalAnalysisError': ('DataAnalysisError', 'Fundamental analysis errors.'),
        'SentimentAnalysisError': ('AIAnalysisError', 'Sentiment analysis errors.'),
        'TrendAnalysisError': ('DataAnalysisError', 'Trend analysis errors.'),
        'VolatilityAnalysisError': ('DataAnalysisError', 'Volatility analysis errors.'),
        
        # Strategy exceptions
        'StrategyAnalysisError': ('StrategyError', 'Strategy analysis errors.'),
        'BacktestingError': ('StrategyError', 'Backtesting errors.'),
        'OptimizationError': ('StrategyError', 'Optimization errors.'),
        'ParameterError': ('StrategyError', 'Parameter validation errors.'),
        'SignalError': ('StrategyError', 'Trading signal errors.'),
        'IndicatorError': ('StrategyError', 'Technical indicator errors.'),
        
        # System exceptions
        'InitializationError': ('SystemError', 'Initialization errors.'),
        'ShutdownError': ('SystemError', 'Shutdown errors.'),
        'StartupError': ('SystemError', 'Startup errors.'),
        'ComponentError': ('SystemError', 'Component errors.'),
        'ServiceError': ('SystemError', 'Service errors.'),
        'ModuleError': ('SystemError', 'Module errors.'),
        
        # Default fallbacks
        'FallbackError': ('TradingBotError', 'Fallback errors.'),
        'UnknownError': ('TradingBotError', 'Unknown errors.'),
        'GenericError': ('TradingBotError', 'Generic errors.'),
    }
    
    for exception_name in missing:
        if exception_name in parent_mapping:
            parent, description = parent_mapping[exception_name]
            exception_definitions.append((exception_name, parent, description))
        else:
            # Try to infer parent class from name
            if 'Analysis' in exception_name:
                parent = 'DataAnalysisError'
                description = f'{exception_name.replace("Error", "")} errors.'
            elif 'Model' in exception_name:
                parent = 'AIAnalysisError'
                description = f'{exception_name.replace("Error", "")} errors.'
            elif 'Contract' in exception_name:
                parent = 'ContractError'
                description = f'{exception_name.replace("Error", "")} errors.'
            elif 'Token' in exception_name:
                parent = 'TokenAnalysisError'
                description = f'{exception_name.replace("Error", "")} errors.'
            elif 'Data' in exception_name:
                parent = 'DataError'
                description = f'{exception_name.replace("Error", "")} errors.'
            elif 'Network' in exception_name:
                parent = 'NetworkError'
                description = f'{exception_name.replace("Error", "")} errors.'
            elif 'Trading' in exception_name:
                parent = 'TradingError'
                description = f'{exception_name.replace("Error", "")} errors.'
            elif 'Validation' in exception_name:
                parent = 'ValidationError'
                description = f'{exception_name.replace("Error", "")} errors.'
            else:
                parent = 'TradingBotError'
                description = f'{exception_name.replace("Error", "")} errors.'
            
            exception_definitions.append((exception_name, parent, description))
    
    return exception_definitions


def add_exceptions_to_file(exceptions: List[Tuple[str, str, str]]) -> bool:
    """Add exceptions to exceptions.py file."""
    
    exceptions_file = Path("app/core/exceptions.py")
    
    if not exceptions_file.exists():
        print("❌ exceptions.py not found")
        return False
    
    try:
        content = exceptions_file.read_text(encoding='utf-8')
        
        # Add each exception
        for exception_name, parent_class, description in exceptions:
            if f"class {exception_name}" not in content:
                new_exception = f'''

class {exception_name}({parent_class}):
    """{description}"""
    pass
'''
                content += new_exception
        
        # Update __all__ list
        if '__all__ = [' in content:
            all_start = content.find("__all__ = [")
            all_end = content.find("]", all_start)
            
            if all_start != -1 and all_end != -1:
                new_entries = ""
                for exception_name, _, _ in exceptions:
                    if f"'{exception_name}'" not in content[all_start:all_end]:
                        new_entries += f"    '{exception_name}',\n"
                
                if new_entries:
                    content = content[:all_end] + new_entries + "    " + content[all_end:]
        
        # Write back
        exceptions_file.write_text(content, encoding='utf-8')
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding exceptions: {e}")
        return False


def main():
    """Scan and fix all exception references."""
    print("🔧 Scanning and Fixing All Exception References")
    print("=" * 60)
    
    # Step 1: Scan for referenced exceptions
    print("1. Scanning Python files for exception references...")
    referenced_exceptions = scan_for_exception_imports()
    print(f"   Found {len(referenced_exceptions)} referenced exceptions")
    
    if referenced_exceptions:
        print("   Referenced exceptions:")
        for exc in sorted(list(referenced_exceptions)[:10]):
            print(f"     - {exc}")
        if len(referenced_exceptions) > 10:
            print(f"     ... and {len(referenced_exceptions) - 10} more")
    
    # Step 2: Get existing exceptions
    print("\n2. Checking existing exceptions...")
    existing_exceptions = get_existing_exceptions()
    print(f"   Found {len(existing_exceptions)} existing exceptions")
    
    # Step 3: Generate missing exceptions
    print("\n3. Generating missing exceptions...")
    missing_exception_defs = generate_missing_exceptions(referenced_exceptions, existing_exceptions)
    print(f"   Need to add {len(missing_exception_defs)} missing exceptions")
    
    if missing_exception_defs:
        print("   Missing exceptions:")
        for exc_name, parent, desc in missing_exception_defs[:10]:
            print(f"     - {exc_name} ({parent})")
        if len(missing_exception_defs) > 10:
            print(f"     ... and {len(missing_exception_defs) - 10} more")
    
    # Step 4: Add missing exceptions
    if missing_exception_defs:
        print("\n4. Adding missing exceptions to exceptions.py...")
        success = add_exceptions_to_file(missing_exception_defs)
        
        if success:
            print(f"✅ Added {len(missing_exception_defs)} missing exceptions")
        else:
            print("❌ Failed to add missing exceptions")
    else:
        print("\n4. No missing exceptions to add")
        success = True
    
    print("\n" + "=" * 60)
    print("Scan and Fix Summary:")
    print("=" * 60)
    
    if success:
        print("✅ All exception references have been resolved!")
        print("\nNext steps:")
        print("1. Run: python test_all_features.py")
        print("2. Should now work without any exception import errors")
    else:
        print("❌ Some exceptions could not be added")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)