import io
from jinja2 import Environment, FileSystemLoader
import yaml
import os
import pandas as pd

path = "glue/scripts/"
# list all file in path
df_files = pd.DataFrame([s[0:-3] for s in os.listdir(path) if s.endswith(".py")], columns=["glue_job_script_name"])
df_files["layer"] = df_files["glue_job_script_name"].str.slice(0, 2)

df_dict = df_files.to_dict(orient="index")

output = io.StringIO()
for key, value in df_dict.items():

    job_param = value
    # load default dev config
    param_dev = yaml.safe_load(open("./dev_param.yml"))
    # merge the dicts
    job_param.update(param_dev)
    # Load Jinja2 template
    env = Environment(loader=FileSystemLoader("./"), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template("gluejob.j2")

    # Render template
    job_out = template.render(job_param)

    # save to file
    file_path_name = f'{path}{job_param.get("glue_job_script_name")}.yml'

    with io.open(file_path_name, "w") as f:
        f.write(job_out)
        f.close()

    # create a new file with merged yaml
    output.write(job_out + "\n")

with io.open("full.yaml", "w") as f:
    f.write(output.getvalue())
    f.close()

output.close()
