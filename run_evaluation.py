import asyncio
from evaluation import list_logs, load_log_file, evaluate_log_record
import pandas as pd
from tqdm import tqdm

async def main():
    print("=== LLM as a Judge Evaluation ===\n")
    
    logs = list_logs()
    if not logs:
        print("No logs found. Run main.py and ask some questions first!")
        return

    print("\nRunning evaluation on latest logs...\n")
    
    eval_results = []
    
    for log_file in tqdm(logs[:20]):        # Evaluate latest 20 logs
        log_record = load_log_file(log_file)
        eval_output = await evaluate_log_record(log_record)
        
        if eval_output:
            row = {
                'log_file': log_file.name,
                'question': log_record.get('messages', [{}])[0],
                'answer': log_record.get('messages', [{}])[-1],
            }
            
            for check in eval_output.checklist:
                row[check.check_name] = check.check_pass
                row[f"{check.check_name}_justification"] = check.justification
            
            row['summary'] = eval_output.summary
            eval_results.append(row)

    # Create DataFrame
    if eval_results:
        df = pd.DataFrame(eval_results)
        print("\n" + "="*80)
        print("EVALUATION RESULTS")
        print("="*80)
        print(df.mean(numeric_only=True).round(3))
        print("\nSummary of checks:")
        for col in df.columns:
            if col.endswith('_pass') or col in ['instructions_follow', 'answer_relevant', 'answer_citations']:
                if col in df.columns:
                    print(f"{col:25}: {df[col].mean():.1%}")
        
        # Save results
        df.to_csv("evaluation_results.csv", index=False)
        print("\n✅ Results saved to evaluation_results.csv")
    else:
        print("No evaluation results generated.")

if __name__ == "__main__":
    asyncio.run(main())