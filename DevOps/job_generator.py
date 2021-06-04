import io
from jinja2 import Environment, FileSystemLoader
import yaml
import os
import pandas as pd

path = "glue/scripts/"
crawlers_path = "glue/crawlers/"
# list all file in path
df_files = pd.DataFrame([s[0:-3] for s in os.listdir(path) if s.endswith(".py")], columns=["glue_job_script_name"])
df_files["layer"] = df_files["glue_job_script_name"].str.slice(0, 2)

df_dict = df_files.to_dict(orient="index")

output = io.StringIO()
for key, value in df_dict.items():

    job_param = value
    job_name = job_param.get("glue_job_script_name")

    # load default dev config
    param_dev = yaml.safe_load(open("./Parameters/dev_param.yml"))

    # update dict for exception
    for k, i in param_dev.items():
        if type(i) is dict:
            exc_value = i.get("exceptions").get(job_name)
            if exc_value is None:
                exc_value = i.get("default")
            exc_dict = k, exc_value
            param_dev[k] = exc_value

    # merge the dicts
    job_param.update(param_dev)
    # Load Jinja2 template
    env = Environment(loader=FileSystemLoader("./"), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template("./Parameters/Templates/gluejob.j2")
    crawler_template = env.get_template("./Parameters/Templates/gluecrawler.j2")

    # Render job template
    job_out = template.render(job_param)

    # save to file
    file_path_name = f'{path}{job_param.get("glue_job_script_name")}.yml'

    with io.open(file_path_name, "w") as f:
        f.write(job_out)
        f.close()

    # create a new file with merged yaml
    output.write(job_out + "\n")

    # CRAWLERS
    # Render crawlers template
    crawler_out = crawler_template.render(job_param)

    # save crawler ymls
    file_path_name = f'{crawlers_path}{job_param.get("glue_job_script_name")}.yml'

    with io.open(file_path_name, "w") as f:
        f.write(crawler_out)
        f.close()

    # create a new file with merged yaml
    output.write(crawler_out + "\n")

    

with io.open("full.yaml", "w") as f:
    f.write(output.getvalue())
    f.close()

output.close()
