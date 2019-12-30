# 简介

本示例为 [使用函数工作流+函数计算轻松构建 ETL 离线数据处理系统](<https://yq.aliyun.com/articles/741105>) 的示例工程。如果您有以下需求希望自建 Serverless 化 ETL 系统，本示例将是您的最佳方案：

- 您的数据处理业务不定时运行，希望在无任务时，不消耗任何资源；
- 您的数据处理需求只有简单的几个步骤，"杀鸡焉用牛刀"？还是自建来的快点；
- 您的数据处理业务流程有较多的自定义步骤，但现成系统灵活性不足，自建才能满足业务需求；
- 您不希望消耗过多精力搭建和维护系统中使用的各类开源数据处理模块，但希望在大并发数据处理请求的场景下能够有较为良好的性能表现。

### 示例场景简介

我们有一批待处理数据，数据的值为 `data_1` 或 `data_2`。我们数据处理的目的是统计各类数据的出现次数，并将统计结果存储到数据仓库中。当数据量级达到一定程度，亦或数据源异构的情况下，我们很难一次性的通过一个进程在短时间内快速处理完成。本示例展示了这一场景下的高效解决方案，利用阿里云函数工作流 + 函数计算的产品组合快速构建 MapReduce 分布式处理框架，实现离线大数据处理的 Serverless 化架构。

### 工程部署

请确保您已开通阿里云对象存储、函数计算、函数工作流服务。我们提供了一键搭建本示例的 [ROS](<https://www.aliyun.com/product/ros>) 描述文件，如果您是初次使用相关服务或阿里云，建议您配置好 [ALIYUN CLI 工具](<https://help.aliyun.com/document_detail/139508.html>) （完成 AK 的配置）后直接在本工程目录下执行下述命令：

```shell
aliyun ros CreateStack --StackName=etl-stack1 --TemplateBody "$(cat ./ros.yaml)" --Parameters.1.ParameterKey=MainAccountID --Parameters.1.ParameterValue={YourAccountID} --Parameters.2.ParameterKey=RandomSuffix --Parameters.2.ParameterValue=stack1 --RegionId=cn-beijing --TimeoutInMinutes=10
```

其中，请将 `{YourAccountID}` 替换为您的主账号ID。"stack1" 参数可以使用随机字符串等自定义参数。

执行该命令后，我们将创建以下资源用于本次示例工程：

- 访问控制 RamRole：用于函数工作流的执行及函数计算的执行；
- 函数工作流（FnF）：创建一个流程，用于执行；
- 函数计算（FC）：创建三个函数，用于实际的数据计算步骤；
- 对象存储（OSS）：创建一个 Bucket，用于存储最终结果。

您也可以通过各服务的控制台手动创建对应资源。其中，函数工作流的流程定义存储于 `./flow/demo-etl-flow.yaml`中，函数计算的函数定义存储于 `./functions` 中。

### 工程演示

确保资源部署完成后，进入[函数工作流控制台](<https://fnf.console.aliyun.com/fnf/cn-beijing/flows>)，选择刚创建的流程，点击开始执行。您可以在控制台查看执行结果。

当流程执行完成后，进入到 OSS 控制台中，查看中间过程及执行结果。

![result](<https://github.com/awesome-fnf/ETL-DataProcessing/blob/master/result.gif>)
