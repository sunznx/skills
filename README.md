# Skills

这个仓库存放我正在使用的 skills。外部更新会经过三方合并，因此仓库里的差异化修改可以保留。

## 使用

```bash
./sync-skills                    # 检查并更新全部外部 skills
./sync-skills <skill-name>       # 只检查并同步指定 skill
./sync-skills 添加 <skill-name>  # 从 ~/.agents/skills 导入一个 skill
./sync-skills 删除 <skill-name>  # 从仓库和本机删除一个 skill
```

- 无参数调用会直接对比全部上游；有更新时合并并 commit。
- 指定 skill 时，只对比该 skill 的上游，并只同步它的仓库快照到本机。
- `添加` 从 `~/.agents/skills` 导入指定 skill，并更新来源目录。
- `删除` 从仓库、来源目录和 `~/.agents/skills` 移除指定 skill。
- 没有冲突时，仓库清单会同步到 `~/.agents/skills`。
- 上游 Git 缓存保存在 `~/.agents/cache/sync-skills`。
- 成功调用后会提交本次同步产生的改动并执行 `git push`；没有改动时不创建空 commit。

出现合并冲突时，脚本会留下冲突标记并停止 commit 和本机同步。

在 agent 对话中，`更新` 表示本地修改 skill，而不是 shell 子命令：

```text
$sync-skills
$sync-skills agent-messaging
$sync-skills 更新 agent-messaging 加入某个功能
$sync-skills 更新 agent-messaging 删除某个功能
```

<!-- skill-catalog:start -->
## Skill 来源目录

| 本仓库 skill | 外部来源 | 外部 skill 路径 | 管理方式 |
| --- | --- | --- | --- |
| `agent-messaging` | 本地维护，暂无外部 Git 来源 | — | 本地维护 |
| `alibabacloud-ack-cli` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/container/csk/alibabacloud-ack-cli/SKILL.md` | 三方合并 |
| `alibabacloud-actiontrail-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-actiontrail-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-aes-ack-pod-performance-profiling` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-aes-ack-pod-performance-profiling/SKILL.md` | 三方合并 |
| `alibabacloud-aes-sysom-lingjun-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-aes-sysom-lingjun-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-aes-sysom-os-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-aes-sysom-os-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-aes-sysom-pai-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-aes-sysom-pai-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-agent-toolkit-install` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/openapiexplorer/alibabacloud-agent-toolkit-install/SKILL.md` | 三方合并 |
| `alibabacloud-agentbay-aio-skills` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/agentbay/alibabacloud-agentbay-aio-skills/SKILL.md` | 三方合并 |
| `alibabacloud-agentloop-contextstore` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/middleware/cms/alibabacloud-agentloop-contextstore/SKILL.md` | 三方合并 |
| `alibabacloud-agentloop-dataset` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/agentloop/alibabacloud-agentloop-dataset/SKILL.md` | 三方合并 |
| `alibabacloud-agentloop-evaluation` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/agentloop/alibabacloud-agentloop-evaluation/SKILL.md` | 三方合并 |
| `alibabacloud-agentloop-experience` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/agentloop/alibabacloud-agentloop-experience/SKILL.md` | 三方合并 |
| `alibabacloud-agentloop-management` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/agentloop/alibabacloud-agentloop-management/SKILL.md` | 三方合并 |
| `alibabacloud-ai-innovation-lab-skill` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/ecs/alibabacloud-ai-innovation-lab-skill/SKILL.md` | 三方合并 |
| `alibabacloud-aidbs-dgate-skill` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/dms/alibabacloud-aidbs-dgate-skill/SKILL.md` | 三方合并 |
| `alibabacloud-aisc-skill-inspection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/asc/alibabacloud-aisc-skill-inspection/SKILL.md` | 三方合并 |
| `alibabacloud-ak-leak-incident-response` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-ak-leak-incident-response/SKILL.md` | 三方合并 |
| `alibabacloud-alb-ingress-doctor` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-alb-ingress-doctor/SKILL.md` | 三方合并 |
| `alibabacloud-alinux-sysom-inspection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/alinux/alibabacloud-alinux-sysom-inspection/SKILL.md` | 三方合并 |
| `alibabacloud-analyticdb-mysql-copilot` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/adb/alibabacloud-analyticdb-mysql-copilot/SKILL.md` | 三方合并 |
| `alibabacloud-analyticdb-postgresql-ai-coaching-best-practice` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/solutions/alibabacloud-analyticdb-postgresql-ai-coaching-best-practice/SKILL.md` | 三方合并 |
| `alibabacloud-analyticdb-postgresql-knowledgebase-ops` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/adb/alibabacloud-analyticdb-postgresql-knowledgebase-ops/SKILL.md` | 三方合并 |
| `alibabacloud-analyticdb-postgresql-supabase-ops` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/gpdb/alibabacloud-analyticdb-postgresql-supabase-ops/SKILL.md` | 三方合并 |
| `alibabacloud-analyticdb-spark-application-analysis-helper` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/ads/alibabacloud-analyticdb-spark-application-analysis-helper/SKILL.md` | 三方合并 |
| `alibabacloud-apigw-inspection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/middleware/apigateway/alibabacloud-apigw-inspection/SKILL.md` | 三方合并 |
| `alibabacloud-avatar-video` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/avatar/alibabacloud-avatar-video/SKILL.md` | 三方合并 |
| `alibabacloud-bailian-image-creator` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/sfm/alibabacloud-bailian-image-creator/SKILL.md` | 三方合并 |
| `alibabacloud-bailian-memory` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/sfm/alibabacloud-bailian-memory/SKILL.md` | 三方合并 |
| `alibabacloud-bailian-rag-knowledgebase` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/sfm/alibabacloud-bailian-rag-knowledgebase/SKILL.md` | 三方合并 |
| `alibabacloud-bailian-video-creator` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/sfm/alibabacloud-bailian-video-creator/SKILL.md` | 三方合并 |
| `alibabacloud-bailian-videoanalysis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/sfm/alibabacloud-bailian-videoanalysis/SKILL.md` | 三方合并 |
| `alibabacloud-bailian-voice-creator` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/sfm/alibabacloud-bailian-voice-creator/SKILL.md` | 三方合并 |
| `alibabacloud-cadt-arch-draw` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/bpstudio/alibabacloud-cadt-arch-draw/SKILL.md` | 三方合并 |
| `alibabacloud-cadt-deploy-on-aliyun` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/bpstudio/alibabacloud-cadt-deploy-on-aliyun/SKILL.md` | 三方合并 |
| `alibabacloud-cadt-probe` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/bpstudio/alibabacloud-cadt-probe/SKILL.md` | 三方合并 |
| `alibabacloud-cas-ssl-cert-deploy` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/cas/alibabacloud-cas-ssl-cert-deploy/SKILL.md` | 三方合并 |
| `alibabacloud-cas-ssl-cert-purchase` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/cas/alibabacloud-cas-ssl-cert-purchase/SKILL.md` | 三方合并 |
| `alibabacloud-cas-ssl-common-tools` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/cas/alibabacloud-cas-ssl-common-tools/SKILL.md` | 三方合并 |
| `alibabacloud-cdn-refresh-preload` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-cdn-refresh-preload/SKILL.md` | 三方合并 |
| `alibabacloud-cdn-traffic-anomaly` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-cdn-traffic-anomaly/SKILL.md` | 三方合并 |
| `alibabacloud-cfw-acl-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-cfw-acl-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-cfw-exposure-detection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/cloudfw/alibabacloud-cfw-exposure-detection/SKILL.md` | 三方合并 |
| `alibabacloud-cfw-internet-firewall-protect` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/cfw/alibabacloud-cfw-internet-firewall-protect/SKILL.md` | 三方合并 |
| `alibabacloud-cfw-ips-event` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/cloudfw/alibabacloud-cfw-ips-event/SKILL.md` | 三方合并 |
| `alibabacloud-cfw-nat-firewall-protect` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/cfw/alibabacloud-cfw-nat-firewall-protect/SKILL.md` | 三方合并 |
| `alibabacloud-cfw-status-overview` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/cloudfw/alibabacloud-cfw-status-overview/SKILL.md` | 三方合并 |
| `alibabacloud-chatapp-message-send` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/entcmc/cams/alibabacloud-chatapp-message-send/SKILL.md` | 三方合并 |
| `alibabacloud-cksync-plan` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/clickhouse/alibabacloud-cksync-plan/SKILL.md` | 三方合并 |
| `alibabacloud-cli-guidance` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/solutions/alibabacloud-cli-guidance/SKILL.md` | 三方合并 |
| `alibabacloud-cloud-native-internet-diagnostics` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-cloud-native-internet-diagnostics/SKILL.md` | 三方合并 |
| `alibabacloud-cloudbackup-ecs-file-backup-essential-edition` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/hbr/alibabacloud-cloudbackup-ecs-file-backup-essential-edition/SKILL.md` | 三方合并 |
| `alibabacloud-cloudfw-vpc-firewall-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-cloudfw-vpc-firewall-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-cms-alert-rule-create` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/middleware/cms/alibabacloud-cms-alert-rule-create/SKILL.md` | 三方合并 |
| `alibabacloud-cms-dataset` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/middleware/cms/alibabacloud-cms-dataset/SKILL.md` | 三方合并 |
| `alibabacloud-cms-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/middleware/cms/alibabacloud-cms-manage/SKILL.md` | 三方合并 |
| `alibabacloud-csas-user-device-ops` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/csas/alibabacloud-csas-user-device-ops/SKILL.md` | 三方合并 |
| `alibabacloud-das-agent` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/hdm/alibabacloud-das-agent/SKILL.md` | 三方合并 |
| `alibabacloud-data-agent-skill` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/dms/alibabacloud-data-agent-skill/SKILL.md` | 三方合并 |
| `alibabacloud-datahub-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/datahub/alibabacloud-datahub-manage/SKILL.md` | 三方合并 |
| `alibabacloud-dataphin-skills` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/dataphin/alibabacloud-dataphin-skills/SKILL.md` | 三方合并 |
| `alibabacloud-dataworks-data-agent` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/dide/alibabacloud-dataworks-data-agent/SKILL.md` | 三方合并 |
| `alibabacloud-dataworks-data-ops` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/dide/alibabacloud-dataworks-data-ops/SKILL.md` | 三方合并 |
| `alibabacloud-dataworks-datastudio-develop` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/dide/alibabacloud-dataworks-datastudio-develop/SKILL.md` | 三方合并 |
| `alibabacloud-dataworks-infra-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/dide/alibabacloud-dataworks-infra-manage/SKILL.md` | 三方合并 |
| `alibabacloud-dataworks-metadata` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/dide/alibabacloud-dataworks-metadata/SKILL.md` | 三方合并 |
| `alibabacloud-dataworks-semantic` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/dide/alibabacloud-dataworks-semantic/SKILL.md` | 三方合并 |
| `alibabacloud-dataworks-workspace-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/dide/alibabacloud-dataworks-workspace-manage/SKILL.md` | 三方合并 |
| `alibabacloud-ddos-native-intercept-query` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/ddos/alibabacloud-ddos-native-intercept-query/SKILL.md` | 三方合并 |
| `alibabacloud-ddos-origin-exposure-detector` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/ddos/alibabacloud-ddos-origin-exposure-detector/SKILL.md` | 三方合并 |
| `alibabacloud-ddos-security-monitor` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/ddos/alibabacloud-ddos-security-monitor/SKILL.md` | 三方合并 |
| `alibabacloud-ddoscoo-domain-configuration-backup` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/ddos/alibabacloud-ddoscoo-domain-configuration-backup/SKILL.md` | 三方合并 |
| `alibabacloud-ddoscoo-intercept-query` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/ddos/alibabacloud-ddoscoo-intercept-query/SKILL.md` | 三方合并 |
| `alibabacloud-devops` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/rdc/alibabacloud-devops/SKILL.md` | 三方合并 |
| `alibabacloud-dlf-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/dlf/alibabacloud-dlf-manage/SKILL.md` | 三方合并 |
| `alibabacloud-dms-data-agent-platform-setup` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/dms/alibabacloud-dms-data-agent-platform-setup/SKILL.md` | 三方合并 |
| `alibabacloud-dms-skill` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/dms/alibabacloud-dms-skill/SKILL.md` | 三方合并 |
| `alibabacloud-dns-resolve-diagnose-customer` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-dns-resolve-diagnose-customer/SKILL.md` | 三方合并 |
| `alibabacloud-docmind-parse` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/docmind/alibabacloud-docmind-parse/SKILL.md` | 三方合并 |
| `alibabacloud-dsc-audit` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/sddp/alibabacloud-dsc-audit/SKILL.md` | 三方合并 |
| `alibabacloud-dts-task-manager` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/dts/alibabacloud-dts-task-manager/SKILL.md` | 三方合并 |
| `alibabacloud-dts-task-query` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-dts-task-query/SKILL.md` | 三方合并 |
| `alibabacloud-ebs-disk-events` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/disk/alibabacloud-ebs-disk-events/SKILL.md` | 三方合并 |
| `alibabacloud-ebs-disk-metric-analyzer` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/disk/alibabacloud-ebs-disk-metric-analyzer/SKILL.md` | 三方合并 |
| `alibabacloud-ebs-disk-snapshot-management` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/disk/alibabacloud-ebs-disk-snapshot-management/SKILL.md` | 三方合并 |
| `alibabacloud-ebs-usage-summary` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/disk/alibabacloud-ebs-usage-summary/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-code-deploy` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/computenest/alibabacloud-ecs-code-deploy/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-diagnose` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/ecs/alibabacloud-ecs-diagnose/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-disaster-recovery-image` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/ecs/alibabacloud-ecs-disaster-recovery-image/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-disaster-recovery-snapshot` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/ecs/alibabacloud-ecs-disaster-recovery-snapshot/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-gpu-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-ecs-gpu-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-health-inspection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-ecs-health-inspection/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-install-extension` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/oos/alibabacloud-ecs-install-extension/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-linux-os-troubleshooting` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/ecs/alibabacloud-ecs-linux-os-troubleshooting/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-patch-management` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/oos/alibabacloud-ecs-patch-management/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-reboot-or-crash-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-ecs-reboot-or-crash-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-vpc-publicnetwork-troubleshoot` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-ecs-vpc-publicnetwork-troubleshoot/SKILL.md` | 三方合并 |
| `alibabacloud-ecs-windows-os-troubleshooting` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/ecs/alibabacloud-ecs-windows-os-troubleshooting/SKILL.md` | 三方合并 |
| `alibabacloud-ehpc-instant-job-skill` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/ehpc/alibabacloud-ehpc-instant-job-skill/SKILL.md` | 三方合并 |
| `alibabacloud-elasticsearch-instance-diagnose` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/elasticsearch/alibabacloud-elasticsearch-instance-diagnose/SKILL.md` | 三方合并 |
| `alibabacloud-elasticsearch-instance-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/elasticsearch/alibabacloud-elasticsearch-instance-manage/SKILL.md` | 三方合并 |
| `alibabacloud-elasticsearch-log-config-generator` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/elasticsearch/alibabacloud-elasticsearch-log-config-generator/SKILL.md` | 三方合并 |
| `alibabacloud-elasticsearch-network-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/elasticsearch/alibabacloud-elasticsearch-network-manage/SKILL.md` | 三方合并 |
| `alibabacloud-emas-apm-query` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/entcmc/emas/alibabacloud-emas-apm-query/SKILL.md` | 三方合并 |
| `alibabacloud-emas-apm-remotelog` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/entcmc/emas/alibabacloud-emas-apm-remotelog/SKILL.md` | 三方合并 |
| `alibabacloud-emr-cluster-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/emapreduce/alibabacloud-emr-cluster-manage/SKILL.md` | 三方合并 |
| `alibabacloud-emr-spark-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/emapreduce/alibabacloud-emr-spark-manage/SKILL.md` | 三方合并 |
| `alibabacloud-emr-starrocks-assistant` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/emapreduce/alibabacloud-emr-starrocks-assistant/SKILL.md` | 三方合并 |
| `alibabacloud-emr-starrocks-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/emapreduce/alibabacloud-emr-starrocks-manage/SKILL.md` | 三方合并 |
| `alibabacloud-error-troubleshoot` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/openapiexplorer/alibabacloud-error-troubleshoot/SKILL.md` | 三方合并 |
| `alibabacloud-esa-pages-deploy` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/netcdn/dcdn/alibabacloud-esa-pages-deploy/SKILL.md` | 三方合并 |
| `alibabacloud-find-skills` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/solutions/alibabacloud-find-skills/SKILL.md` | 三方合并 |
| `alibabacloud-finops-inspect` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/accs/alibabacloud-finops-inspect/SKILL.md` | 三方合并 |
| `alibabacloud-flink-instance-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/sc/alibabacloud-flink-instance-manage/SKILL.md` | 三方合并 |
| `alibabacloud-flink-knowledge` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/sc/alibabacloud-flink-knowledge/SKILL.md` | 三方合并 |
| `alibabacloud-flink-python-coding` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/sc/alibabacloud-flink-python-coding/SKILL.md` | 三方合并 |
| `alibabacloud-flink-workspace-ops` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/sc/alibabacloud-flink-workspace-ops/SKILL.md` | 三方合并 |
| `alibabacloud-governance-evaluation-report` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/governance/alibabacloud-governance-evaluation-report/SKILL.md` | 三方合并 |
| `alibabacloud-help-doc-search` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-help-doc-search/SKILL.md` | 三方合并 |
| `alibabacloud-history-lock-diagnose` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-history-lock-diagnose/SKILL.md` | 三方合并 |
| `alibabacloud-hologres-instance-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/hologram/alibabacloud-hologres-instance-manage/SKILL.md` | 三方合并 |
| `alibabacloud-iac-code` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/ros/alibabacloud-iac-code/SKILL.md` | 三方合并 |
| `alibabacloud-icpba-sucessdata-query` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/doweb/companyreg/alibabacloud-icpba-sucessdata-query/SKILL.md` | 三方合并 |
| `alibabacloud-iqs-search` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/entcmc/alibababcp/alibabacloud-iqs-search/SKILL.md` | 三方合并 |
| `alibabacloud-iqs-weather-query` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/solutions/alibabacloud-iqs-weather-query/SKILL.md` | 三方合并 |
| `alibabacloud-kafka-capacity-assessment` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-kafka-capacity-assessment/SKILL.md` | 三方合并 |
| `alibabacloud-kms-secret-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/kms/alibabacloud-kms-secret-manage/SKILL.md` | 三方合并 |
| `alibabacloud-kvstore-health-inspection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-kvstore-health-inspection/SKILL.md` | 三方合并 |
| `alibabacloud-lb-healthcheck` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-lb-healthcheck/SKILL.md` | 三方合并 |
| `alibabacloud-lindorm-agent-skill` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/hitsdb/alibabacloud-lindorm-agent-skill/SKILL.md` | 三方合并 |
| `alibabacloud-livedebug` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/middleware/arms/alibabacloud-livedebug/SKILL.md` | 三方合并 |
| `alibabacloud-liverecord-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/mediaservices/live/alibabacloud-liverecord-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-loongcollector-ops` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/sls/alibabacloud-loongcollector-ops/SKILL.md` | 三方合并 |
| `alibabacloud-maxcompute-migration-service` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/odps/alibabacloud-maxcompute-migration-service/SKILL.md` | 三方合并 |
| `alibabacloud-maxframe-video-frame-pipeline` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/odps/alibabacloud-maxframe-video-frame-pipeline/SKILL.md` | 三方合并 |
| `alibabacloud-mcp-core-script-generate` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/solutions/alibabacloud-mcp-core-script-generate/SKILL.md` | 三方合并 |
| `alibabacloud-media-diagnostics` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-media-diagnostics/SKILL.md` | 三方合并 |
| `alibabacloud-migration-db-evaluation-collector` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/wadaps/alibabacloud-migration-db-evaluation-collector/SKILL.md` | 三方合并 |
| `alibabacloud-migration-dbm-oracle-traffic-capture` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/wadaps/alibabacloud-migration-dbm-oracle-traffic-capture/SKILL.md` | 三方合并 |
| `alibabacloud-migration-dbm-redis-shake-migration` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/wadaps/alibabacloud-migration-dbm-redis-shake-migration/SKILL.md` | 三方合并 |
| `alibabacloud-migration-lhm-inspect-hive-metastore` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/wadaps/alibabacloud-migration-lhm-inspect-hive-metastore/SKILL.md` | 三方合并 |
| `alibabacloud-migration-lhm-migrate-hive-to-paimon` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/wadaps/alibabacloud-migration-lhm-migrate-hive-to-paimon/SKILL.md` | 三方合并 |
| `alibabacloud-migration-mas-cloud-migration-survey` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/wadaps/alibabacloud-migration-mas-cloud-migration-survey/SKILL.md` | 三方合并 |
| `alibabacloud-migration-mas-product-mapping` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/wadaps/alibabacloud-migration-mas-product-mapping/SKILL.md` | 三方合并 |
| `alibabacloud-migration-mas-solution` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/wadaps/alibabacloud-migration-mas-solution/SKILL.md` | 三方合并 |
| `alibabacloud-migration-sdm-sql-trans` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/wadaps/alibabacloud-migration-sdm-sql-trans/SKILL.md` | 三方合并 |
| `alibabacloud-milvus-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/milvus/alibabacloud-milvus-manage/SKILL.md` | 三方合并 |
| `alibabacloud-mining-attack-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-mining-attack-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-mongodb-instances-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/mongodb/alibabacloud-mongodb-instances-manage/SKILL.md` | 三方合并 |
| `alibabacloud-mse-nacos-inspection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-mse-nacos-inspection/SKILL.md` | 三方合并 |
| `alibabacloud-mtr-network-diagnosis-customer` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-mtr-network-diagnosis-customer/SKILL.md` | 三方合并 |
| `alibabacloud-nas-mount-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-nas-mount-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-network-diagnose` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-network-diagnose/SKILL.md` | 三方合并 |
| `alibabacloud-network-health-inspection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-network-health-inspection/SKILL.md` | 三方合并 |
| `alibabacloud-network-reachability-analysis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/netcdn/netana/alibabacloud-network-reachability-analysis/SKILL.md` | 三方合并 |
| `alibabacloud-nginx-ingress-to-api-gateway` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/middleware/apigateway/alibabacloud-nginx-ingress-to-api-gateway/SKILL.md` | 三方合并 |
| `alibabacloud-odps-cost-analysis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/odps/alibabacloud-odps-cost-analysis/SKILL.md` | 三方合并 |
| `alibabacloud-odps-information-schema` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/odps/alibabacloud-odps-information-schema/SKILL.md` | 三方合并 |
| `alibabacloud-odps-maxframe-coding` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/odps/alibabacloud-odps-maxframe-coding/SKILL.md` | 三方合并 |
| `alibabacloud-odps-project-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/odps/alibabacloud-odps-project-manage/SKILL.md` | 三方合并 |
| `alibabacloud-odps-quota-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/odps/alibabacloud-odps-quota-manage/SKILL.md` | 三方合并 |
| `alibabacloud-odps-sql-generation` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/odps/alibabacloud-odps-sql-generation/SKILL.md` | 三方合并 |
| `alibabacloud-oos-chatops-agent` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/oos/alibabacloud-oos-chatops-agent/SKILL.md` | 三方合并 |
| `alibabacloud-oos-template-generation` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/oos/alibabacloud-oos-template-generation/SKILL.md` | 三方合并 |
| `alibabacloud-opc-advisor` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/ecs/alibabacloud-opc-advisor/SKILL.md` | 三方合并 |
| `alibabacloud-opc-deploy` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/ecs/alibabacloud-opc-deploy/SKILL.md` | 三方合并 |
| `alibabacloud-openclaw-ecs-dingtalk` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/solutions/alibabacloud-openclaw-ecs-dingtalk/SKILL.md` | 三方合并 |
| `alibabacloud-openclaw-skill-security-scan` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/riskmanagement/alibabacloud-openclaw-skill-security-scan/SKILL.md` | 三方合并 |
| `alibabacloud-opensearch-app-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/opensearch/alibabacloud-opensearch-app-manage/SKILL.md` | 三方合并 |
| `alibabacloud-oss-manage-cron-upload` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/oss/alibabacloud-oss-manage-cron-upload/SKILL.md` | 三方合并 |
| `alibabacloud-oss-manage-metaquery` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/oss/alibabacloud-oss-manage-metaquery/SKILL.md` | 三方合并 |
| `alibabacloud-oss-manage-network-probe` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/oss/alibabacloud-oss-manage-network-probe/SKILL.md` | 三方合并 |
| `alibabacloud-oss-media-process` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/oss/alibabacloud-oss-media-process/SKILL.md` | 三方合并 |
| `alibabacloud-pai-dlc-job` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-dlc-job/SKILL.md` | 三方合并 |
| `alibabacloud-pai-dlc-job-diagnostics` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-dlc-job-diagnostics/SKILL.md` | 三方合并 |
| `alibabacloud-pai-dsw-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-dsw-manage/SKILL.md` | 三方合并 |
| `alibabacloud-pai-eas-service-deploy` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-eas-service-deploy/SKILL.md` | 三方合并 |
| `alibabacloud-pai-eas-service-diagnose` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-eas-service-diagnose/SKILL.md` | 三方合并 |
| `alibabacloud-pai-feature-store-featuredb-usage-query` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-feature-store-featuredb-usage-query/SKILL.md` | 三方合并 |
| `alibabacloud-pai-node-management` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-node-management/SKILL.md` | 三方合并 |
| `alibabacloud-pai-quota-management` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-quota-management/SKILL.md` | 三方合并 |
| `alibabacloud-pai-rec-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-rec-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-pai-resource-group-management` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-resource-group-management/SKILL.md` | 三方合并 |
| `alibabacloud-pai-workspace-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/aiml/learn/alibabacloud-pai-workspace-manage/SKILL.md` | 三方合并 |
| `alibabacloud-pcap-analyzer` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-pcap-analyzer/SKILL.md` | 三方合并 |
| `alibabacloud-pds-intelligent-workspace` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/pds/alibabacloud-pds-intelligent-workspace/SKILL.md` | 三方合并 |
| `alibabacloud-pds-multimodal-search` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/pds/alibabacloud-pds-multimodal-search/SKILL.md` | 三方合并 |
| `alibabacloud-polardb-ai-assistant` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/polardb/alibabacloud-polardb-ai-assistant/SKILL.md` | 三方合并 |
| `alibabacloud-polardb-mysql-inspection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-polardb-mysql-inspection/SKILL.md` | 三方合并 |
| `alibabacloud-polardb-mysql-sql-lint` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-polardb-mysql-sql-lint/SKILL.md` | 三方合并 |
| `alibabacloud-polardbx-ai-assistant` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/drds/alibabacloud-polardbx-ai-assistant/SKILL.md` | 三方合并 |
| `alibabacloud-polardbx-ops` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/drds/alibabacloud-polardbx-ops/SKILL.md` | 三方合并 |
| `alibabacloud-polardbx-sql` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/drds/alibabacloud-polardbx-sql/SKILL.md` | 三方合并 |
| `alibabacloud-pts-ops` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/middleware/pts/alibabacloud-pts-ops/SKILL.md` | 三方合并 |
| `alibabacloud-pts-pilot` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/optdes/alibabacloud-pts-pilot/SKILL.md` | 三方合并 |
| `alibabacloud-pts-reporter` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/optdes/alibabacloud-pts-reporter/SKILL.md` | 三方合并 |
| `alibabacloud-pts-task` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/optdes/alibabacloud-pts-task/SKILL.md` | 三方合并 |
| `alibabacloud-qianwenai-support` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-qianwenai-support/SKILL.md` | 三方合并 |
| `alibabacloud-quickbi-smartq` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/analyticscomputing/quickbi/alibabacloud-quickbi-smartq/SKILL.md` | 三方合并 |
| `alibabacloud-ram-permission-diagnose` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/ram/alibabacloud-ram-permission-diagnose/SKILL.md` | 三方合并 |
| `alibabacloud-rds-copilot` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/rds/alibabacloud-rds-copilot/SKILL.md` | 三方合并 |
| `alibabacloud-rds-instances-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/rds/alibabacloud-rds-instances-manage/SKILL.md` | 三方合并 |
| `alibabacloud-rds-mysql-inspection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-rds-mysql-inspection/SKILL.md` | 三方合并 |
| `alibabacloud-rds-postgresql-inspection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-rds-postgresql-inspection/SKILL.md` | 三方合并 |
| `alibabacloud-remote-skills-connector` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/skillsexplorer/alibabacloud-remote-skills-connector/SKILL.md` | 三方合并 |
| `alibabacloud-resourcecenter-search` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/entconsole/alibabacloud-resourcecenter-search/SKILL.md` | 三方合并 |
| `alibabacloud-ros-agent` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/ros/alibabacloud-ros-agent/SKILL.md` | 三方合并 |
| `alibabacloud-safety-checker` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/lvwang/alibabacloud-safety-checker/SKILL.md` | 三方合并 |
| `alibabacloud-sas-alert-handler` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/sas/alibabacloud-sas-alert-handler/SKILL.md` | 三方合并 |
| `alibabacloud-sas-incident-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/sas/alibabacloud-sas-incident-manage/SKILL.md` | 三方合并 |
| `alibabacloud-sas-install-agent` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/sas/alibabacloud-sas-install-agent/SKILL.md` | 三方合并 |
| `alibabacloud-sas-log-to-oss` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/sas/alibabacloud-sas-log-to-oss/SKILL.md` | 三方合并 |
| `alibabacloud-sas-malware-detection` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/sas/alibabacloud-sas-malware-detection/SKILL.md` | 三方合并 |
| `alibabacloud-sas-multiaccount-manage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/sas/alibabacloud-sas-multiaccount-manage/SKILL.md` | 三方合并 |
| `alibabacloud-sas-openclaw-security` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/sas/alibabacloud-sas-openclaw-security/SKILL.md` | 三方合并 |
| `alibabacloud-sas-overview` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/sas/alibabacloud-sas-overview/SKILL.md` | 三方合并 |
| `alibabacloud-security-health-check` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/solutions/alibabacloud-security-health-check/SKILL.md` | 三方合并 |
| `alibabacloud-security-vuln-coverage-check` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/sas/alibabacloud-security-vuln-coverage-check/SKILL.md` | 三方合并 |
| `alibabacloud-sls-agent-workflow` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/sls/alibabacloud-sls-agent-workflow/SKILL.md` | 三方合并 |
| `alibabacloud-sls-data-agent` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/sls/alibabacloud-sls-data-agent/SKILL.md` | 三方合并 |
| `alibabacloud-sls-index-config-management` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/sls/alibabacloud-sls-index-config-management/SKILL.md` | 三方合并 |
| `alibabacloud-sls-query` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/sls/alibabacloud-sls-query/SKILL.md` | 三方合并 |
| `alibabacloud-sls-sdk-guidance` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/sls/alibabacloud-sls-sdk-guidance/SKILL.md` | 三方合并 |
| `alibabacloud-smartag-pilot` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/netcdn/smartag/alibabacloud-smartag-pilot/SKILL.md` | 三方合并 |
| `alibabacloud-sms-send-short-message` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/entcmc/dysms/alibabacloud-sms-send-short-message/SKILL.md` | 三方合并 |
| `alibabacloud-solution-deploy` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/solutions/alibabacloud-solution-deploy/SKILL.md` | 三方合并 |
| `alibabacloud-sre-toolkit` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/playbooks/trouboper/alibabacloud-sre-toolkit/SKILL.md` | 三方合并 |
| `alibabacloud-starops-chat` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/middleware/starops/alibabacloud-starops-chat/SKILL.md` | 三方合并 |
| `alibabacloud-sysom-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/computing/alinux/alibabacloud-sysom-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-tablestore-agent-storage` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/ots/alibabacloud-tablestore-agent-storage/SKILL.md` | 三方合并 |
| `alibabacloud-tablestore-openclaw-memory` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/ots/alibabacloud-tablestore-openclaw-memory/SKILL.md` | 三方合并 |
| `alibabacloud-tablestore-ops` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/storage/ots/alibabacloud-tablestore-ops/SKILL.md` | 三方合并 |
| `alibabacloud-tair-ai-assistant` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/kvstore/alibabacloud-tair-ai-assistant/SKILL.md` | 三方合并 |
| `alibabacloud-tair-devtoolset` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/database/kvstore/alibabacloud-tair-devtoolset/SKILL.md` | 三方合并 |
| `alibabacloud-terraform-code-generation` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/solutions/alibabacloud-terraform-code-generation/SKILL.md` | 三方合并 |
| `alibabacloud-terraform-import` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/migrationom/solutions/alibabacloud-terraform-import/SKILL.md` | 三方合并 |
| `alibabacloud-tls-cert-diagnosis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-tls-cert-diagnosis/SKILL.md` | 三方合并 |
| `alibabacloud-video-editor` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/mediaservices/ice/alibabacloud-video-editor/SKILL.md` | 三方合并 |
| `alibabacloud-video-forge` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/mediaservices/mts/alibabacloud-video-forge/SKILL.md` | 三方合并 |
| `alibabacloud-video-prompt-architect` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/mediaservices/solutions/alibabacloud-video-prompt-architect/SKILL.md` | 三方合并 |
| `alibabacloud-video-translation` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/mediaservices/ice/alibabacloud-video-translation/SKILL.md` | 三方合并 |
| `alibabacloud-vms-smart-call-by-tts` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/entcmc/dyvms/alibabacloud-vms-smart-call-by-tts/SKILL.md` | 三方合并 |
| `alibabacloud-waf-billing-backup` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-waf-billing-backup/SKILL.md` | 三方合并 |
| `alibabacloud-waf-bot-management` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/waf/alibabacloud-waf-bot-management/SKILL.md` | 三方合并 |
| `alibabacloud-waf-checkresponse-intercept-query` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/waf/alibabacloud-waf-checkresponse-intercept-query/SKILL.md` | 三方合并 |
| `alibabacloud-waf-cname-config-export` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/waf/alibabacloud-waf-cname-config-export/SKILL.md` | 三方合并 |
| `alibabacloud-waf-config-backup` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/waf/alibabacloud-waf-config-backup/SKILL.md` | 三方合并 |
| `alibabacloud-waf-lua-extension-dev` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/waf/alibabacloud-waf-lua-extension-dev/SKILL.md` | 三方合并 |
| `alibabacloud-waf-protectionconfig-backup` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/waf/alibabacloud-waf-protectionconfig-backup/SKILL.md` | 三方合并 |
| `alibabacloud-waf-quick-showcase` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/waf/alibabacloud-waf-quick-showcase/SKILL.md` | 三方合并 |
| `alibabacloud-waf-report` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/waf/alibabacloud-waf-report/SKILL.md` | 三方合并 |
| `alibabacloud-waf-rule-effectiveness-check` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/waf/alibabacloud-waf-rule-effectiveness-check/SKILL.md` | 三方合并 |
| `alibabacloud-waf-rule-management` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/devopsimpl/alibabacloud-waf-rule-management/SKILL.md` | 三方合并 |
| `alibabacloud-waf-security-monitor` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/security/waf/alibabacloud-waf-security-monitor/SKILL.md` | 三方合并 |
| `alibabacloud-web-application-attacks-analysis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-web-application-attacks-analysis/SKILL.md` | 三方合并 |
| `alibabacloud-website-malware-check` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-website-malware-check/SKILL.md` | 三方合并 |
| `alibabacloud-website-probe` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/others/cseskillshub/alibabacloud-website-probe/SKILL.md` | 三方合并 |
| `alibabacloud-workbench-cli` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/solutions/alibabacloud-workbench-cli/SKILL.md` | 三方合并 |
| `alibabacloud-wxz-website-builder` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/doweb/website/alibabacloud-wxz-website-builder/SKILL.md` | 三方合并 |
| `alibabacloud-yike-cli` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/mediaservices/yike/alibabacloud-yike-cli/SKILL.md` | 三方合并 |
| `alibabacloud-yike-storyboard` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/mediaservices/yike/alibabacloud-yike-storyboard/SKILL.md` | 三方合并 |
| `alibabacloud-yunxiao-flow-analysis` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/rdc/alibabacloud-yunxiao-flow-analysis/SKILL.md` | 三方合并 |
| `codebase-design` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/codebase-design/SKILL.md` | 三方合并 |
| `cua-driver` | 本机链接 ~/.cua-driver/skills/cua-driver，仓库保留快照但不覆盖该链接 | — | 仅仓库维护 |
| `diagram-design` | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | `skills/diagram-design/SKILL.md` | 三方合并 |
| `domain-modeling` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/domain-modeling/SKILL.md` | 三方合并 |
| `eli5` | [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | `eli5/skills/eli5/SKILL.md` | 三方合并 |
| `human-context-rebuild` | [lycfyi/yskills](https://github.com/lycfyi/yskills) | `skills/human-context-rebuild/SKILL.md` | 三方合并 |
| `improve-codebase-architecture` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/improve-codebase-architecture/SKILL.md` | 三方合并 |
| `lark-approval` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-approval/SKILL.md` | 三方合并 |
| `lark-attendance` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-attendance/SKILL.md` | 三方合并 |
| `lark-base` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-base/SKILL.md` | 三方合并 |
| `lark-calendar` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-calendar/SKILL.md` | 三方合并 |
| `lark-contact` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-contact/SKILL.md` | 三方合并 |
| `lark-doc` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-doc/SKILL.md` | 三方合并 |
| `lark-drive` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-drive/SKILL.md` | 三方合并 |
| `lark-event` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-event/SKILL.md` | 三方合并 |
| `lark-im` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-im/SKILL.md` | 三方合并 |
| `lark-mail` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-mail/SKILL.md` | 三方合并 |
| `lark-markdown` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-markdown/SKILL.md` | 三方合并 |
| `lark-minutes` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-minutes/SKILL.md` | 三方合并 |
| `lark-okr` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-okr/SKILL.md` | 三方合并 |
| `lark-openapi-explorer` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-openapi-explorer/SKILL.md` | 三方合并 |
| `lark-shared` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-shared/SKILL.md` | 三方合并 |
| `lark-sheets` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-sheets/SKILL.md` | 三方合并 |
| `lark-skill-maker` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-skill-maker/SKILL.md` | 三方合并 |
| `lark-slides` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-slides/SKILL.md` | 三方合并 |
| `lark-task` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-task/SKILL.md` | 三方合并 |
| `lark-vc` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-vc/SKILL.md` | 三方合并 |
| `lark-whiteboard` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-whiteboard/SKILL.md` | 三方合并 |
| `lark-wiki` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-wiki/SKILL.md` | 三方合并 |
| `lark-workflow-meeting-summary` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-workflow-meeting-summary/SKILL.md` | 三方合并 |
| `lark-workflow-standup-report` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-workflow-standup-report/SKILL.md` | 三方合并 |
| `opencli-adapter-author` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-adapter-author/SKILL.md` | 三方合并 |
| `opencli-autofix` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-autofix/SKILL.md` | 三方合并 |
| `opencli-browser` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-browser/SKILL.md` | 三方合并 |
| `opencli-browser-sitemap` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-browser-sitemap/SKILL.md` | 三方合并 |
| `opencli-sitemap-author` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-sitemap-author/SKILL.md` | 三方合并 |
| `opencli-usage` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-usage/SKILL.md` | 三方合并 |
| `planning-with-files` | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | `.agents/skills/planning-with-files/SKILL.md` | 三方合并（仅仓库） |
| `prototype` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/prototype/SKILL.md` | 三方合并 |
| `ra-人话` | [Pluviobyte/rnskill](https://github.com/Pluviobyte/rnskill) | `skills/ra-人话/SKILL.md` | 三方合并 |
| `resolve-merge-conflicts` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/resolve-merge-conflicts/SKILL.md` | 三方合并 |
| `skill-doctor` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/skill-doctor/SKILL.md` | 三方合并 |
| `smart-search` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/smart-search/SKILL.md` | 三方合并 |
| `spec-bootstrap` | 本地维护，安装项目级 Ponytail、PWF skill 与官方 hooks，并配置 Serena、Semble | — | 本地维护 |
| `sync-skills` | 本仓库维护的同步 skill | — | 本地维护 |
| `update-skill` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/update-skill/SKILL.md` | 三方合并 |
| `wait-what` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/wait-what/SKILL.md` | 三方合并 |
| `whats-next` | [lycfyi/yskills](https://github.com/lycfyi/yskills) | `skills/whats-next/SKILL.md` | 三方合并 |
| `writing-for-agents` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/writing-for-agents/SKILL.md` | 三方合并 |
<!-- skill-catalog:end -->
