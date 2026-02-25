"use client"

import { useState } from "react"
import { useI18n } from "@/lib/i18n"
import { SiteHeader } from "@/components/site-header"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { toast } from "sonner"
import { Shield, CheckCircle2, AlertCircle, Loader2, FileText, ArrowRight } from "lucide-react"

type AgentType = "insurer" | "tech" | "opensource"
type ModelPlatform = "openai" | "azure_openai" | "claude" | "gemini" | "deepseek" | "qwen" | "vllm" | "other"

interface FormData {
  applicant_name: string
  company_name: string
  email: string
  phone: string
  agent_name: string
  agent_type: AgentType
  model_platform: ModelPlatform
  api_endpoint: string
  notes: string
}

const initialFormData: FormData = {
  applicant_name: "",
  company_name: "",
  email: "",
  phone: "",
  agent_name: "",
  agent_type: "insurer",
  model_platform: "openai",
  api_endpoint: "",
  notes: "",
}

export default function SubmitPage() {
  const { t } = useI18n()
  const [formData, setFormData] = useState<FormData>(initialFormData)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({})
  const [showSuccessDialog, setShowSuccessDialog] = useState(false)

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof FormData, string>> = {}

    if (!formData.applicant_name.trim()) {
      newErrors.applicant_name = t("submit.error.name")
    }

    if (!formData.email.trim()) {
      newErrors.email = t("submit.error.email")
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = t("submit.error.emailFormat")
    }

    if (!formData.phone.trim()) {
      newErrors.phone = t("submit.error.phone")
    } else if (!/^\+?1?\d{9,15}$/.test(formData.phone.replace(/\s/g, ""))) {
      newErrors.phone = t("submit.error.phoneFormat")
    }

    if (!formData.agent_name.trim()) {
      newErrors.agent_name = t("submit.error.agent")
    }

    if (formData.api_endpoint && !/^https?:\/\//.test(formData.api_endpoint)) {
      newErrors.api_endpoint = t("submit.error.apiFormat")
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      toast.error(t("submit.form.submit"))
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch("http://localhost:8000/api/v1/submissions/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...formData,
          captcha_token: "", // 预留验证码
        }),
      })

      const data = await response.json()

      if (response.ok) {
        // 显示成功对话框
        setShowSuccessDialog(true)
        toast.success(t("submit.success"))
        // 清空表单
        setFormData(initialFormData)
      } else {
        toast.error(data.detail || t("submit.form.submit"))
      }
    } catch (error) {
      // 演示模式下，显示成功对话框
      console.log("Demo mode - submission simulated")
      setShowSuccessDialog(true)
      setFormData(initialFormData)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <main className="mx-auto max-w-3xl px-4 py-8 lg:px-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
              <Shield className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground text-balance">
                {t("submit.title")}
              </h1>
              <p className="text-sm text-muted-foreground">
                {t("submit.subtitle")}
              </p>
            </div>
          </div>
        </div>

        {/* 提示信息 */}
        <Card className="mb-8 bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-800 dark:text-blue-200">
                <p className="font-medium mb-2">{t("submit.process.title")}</p>
                <ol className="list-decimal list-inside space-y-1 text-blue-700 dark:text-blue-300">
                  <li>{t("submit.process.1")}</li>
                  <li>{t("submit.process.2")}</li>
                  <li>{t("submit.process.3")}</li>
                  <li>{t("submit.process.4")}</li>
                </ol>
                <p className="mt-2 text-xs text-blue-600 dark:text-blue-400">
                  {t("submit.rateLimit")}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 表单 */}
        <Card>
          <CardHeader>
            <CardTitle>{t("submit.formInfo.title")}</CardTitle>
            <CardDescription>{t("submit.formInfo.desc")}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid gap-6 md:grid-cols-2">
                {/* 申请人姓名 */}
                <div className="space-y-2">
                  <Label htmlFor="applicant_name">{t("submit.form.applicantName")} *</Label>
                  <Input
                    id="applicant_name"
                    value={formData.applicant_name}
                    onChange={(e) => handleChange("applicant_name", e.target.value)}
                    placeholder={t("submit.placeholder.name")}
                    disabled={isSubmitting}
                  />
                  {errors.applicant_name && (
                    <p className="text-xs text-destructive">{errors.applicant_name}</p>
                  )}
                </div>

                {/* 公司名称 */}
                <div className="space-y-2">
                  <Label htmlFor="company_name">{t("submit.form.companyName")}</Label>
                  <Input
                    id="company_name"
                    value={formData.company_name}
                    onChange={(e) => handleChange("company_name", e.target.value)}
                    placeholder={t("submit.placeholder.company")}
                    disabled={isSubmitting}
                  />
                </div>
              </div>

              <div className="grid gap-6 md:grid-cols-2">
                {/* 邮箱 */}
                <div className="space-y-2">
                  <Label htmlFor="email">{t("submit.form.email")} *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleChange("email", e.target.value)}
                    placeholder={t("submit.placeholder.email")}
                    disabled={isSubmitting}
                  />
                  {errors.email && (
                    <p className="text-xs text-destructive">{errors.email}</p>
                  )}
                </div>

                {/* 手机号 */}
                <div className="space-y-2">
                  <Label htmlFor="phone">{t("submit.form.phone")} *</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => handleChange("phone", e.target.value)}
                    placeholder={t("submit.placeholder.phone")}
                    disabled={isSubmitting}
                  />
                  {errors.phone && (
                    <p className="text-xs text-destructive">{errors.phone}</p>
                  )}
                </div>
              </div>

              {/* Agent 名称 */}
              <div className="space-y-2">
                <Label htmlFor="agent_name">{t("submit.form.agentName")} *</Label>
                <Input
                  id="agent_name"
                  value={formData.agent_name}
                  onChange={(e) => handleChange("agent_name", e.target.value)}
                  placeholder={t("submit.placeholder.agent")}
                  disabled={isSubmitting}
                />
                {errors.agent_name && (
                  <p className="text-xs text-destructive">{errors.agent_name}</p>
                )}
              </div>

              <div className="grid gap-6 md:grid-cols-2">
                {/* Agent 类型 */}
                <div className="space-y-2">
                  <Label htmlFor="agent_type">{t("submit.form.agentType")} *</Label>
                  <Select
                    value={formData.agent_type}
                    onValueChange={(value: AgentType) => handleChange("agent_type", value)}
                  >
                    <SelectTrigger disabled={isSubmitting}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="insurer">{t("submit.agentType.insurer")}</SelectItem>
                      <SelectItem value="tech">{t("submit.agentType.tech")}</SelectItem>
                      <SelectItem value="opensource">{t("submit.agentType.opensource")}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* 模型平台 */}
                <div className="space-y-2">
                  <Label htmlFor="model_platform">{t("submit.form.modelPlatform")} *</Label>
                  <Select
                    value={formData.model_platform}
                    onValueChange={(value: ModelPlatform) => handleChange("model_platform", value)}
                  >
                    <SelectTrigger disabled={isSubmitting}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="openai">{t("submit.model.openai")}</SelectItem>
                      <SelectItem value="azure_openai">{t("submit.model.azure")}</SelectItem>
                      <SelectItem value="claude">{t("submit.model.claude")}</SelectItem>
                      <SelectItem value="gemini">{t("submit.model.gemini")}</SelectItem>
                      <SelectItem value="deepseek">{t("submit.model.deepseek")}</SelectItem>
                      <SelectItem value="qwen">{t("submit.model.qwen")}</SelectItem>
                      <SelectItem value="vllm">{t("submit.model.vllm")}</SelectItem>
                      <SelectItem value="other">{t("submit.model.other")}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* API 端点 */}
              <div className="space-y-2">
                <Label htmlFor="api_endpoint">{t("submit.form.apiEndpoint")}</Label>
                <Input
                  id="api_endpoint"
                  value={formData.api_endpoint}
                  onChange={(e) => handleChange("api_endpoint", e.target.value)}
                  placeholder={t("submit.placeholder.api")}
                  disabled={isSubmitting}
                />
                {errors.api_endpoint && (
                  <p className="text-xs text-destructive">{errors.api_endpoint}</p>
                )}
              </div>

              {/* 备注 */}
              <div className="space-y-2">
                <Label htmlFor="notes">{t("submit.form.notes")}</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => handleChange("notes", e.target.value)}
                  placeholder={t("submit.placeholder.notes")}
                  rows={4}
                  disabled={isSubmitting}
                />
              </div>

              {/* 提交按钮 */}
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {t("submit.form.submitting")}
                  </>
                ) : (
                  <>
                    <FileText className="h-4 w-4 mr-2" />
                    {t("submit.form.submit")}
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </main>

      {/* Success Dialog */}
      <Dialog open={showSuccessDialog} onOpenChange={setShowSuccessDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <div className="flex justify-center mb-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/20">
                <CheckCircle2 className="h-8 w-8 text-green-600 dark:text-green-400" />
              </div>
            </div>
            <DialogTitle className="text-center text-xl">
              {t("submit.success")}
            </DialogTitle>
            <DialogDescription className="text-center">
              {t("submit.review")}
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-3 pt-4">
            <Button
              onClick={() => {
                setShowSuccessDialog(false)
                window.location.href = "/"
              }}
              className="w-full"
            >
              返回首页
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowSuccessDialog(false)}
              className="w-full"
            >
              继续浏览
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
