from airflow.sdk import dag, task
import pendulum


@dag(
    dag_id="assignment3",
    schedule=None,
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    tags=["assignment3" ,"test"],
)
def whole_pipeline():

    @task
    def start_pipe():
        print("Starting Research Paper Library Pipeline")
        return "Pipeline started successfully"

    @task
    def process_pdfs(message):
        print(message)
        print("Starting PDF processing")

    @task
    def finish_pipe():
        print("Research Library Pipeline completed")

    start = start_pipe()
    process = process_pdfs(start)
    finish = finish_pipe()

    process >> finish


whole_pipeline()
