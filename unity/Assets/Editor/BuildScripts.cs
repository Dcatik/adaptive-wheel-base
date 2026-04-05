using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;

public static class BuildScripts
{
    private static string RepoRoot()
    {
        return Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
    }

    private static string BuildOutputRoot()
    {
        return Path.Combine(RepoRoot(), "artifacts", "unity_builds");
    }

    private static string TimeStamp()
    {
        return DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
    }

    private static void EnsureDirectory(string path)
    {
        if (!Directory.Exists(path))
        {
            Directory.CreateDirectory(path);
        }
    }

    public static void BuildLinuxHeadless()
    {
        RunBuild(isHeadless: true);
    }

    public static void BuildLinuxVisual()
    {
        RunBuild(isHeadless: false);
    }

    private static void RunBuild(bool isHeadless)
    {
        string[] scenes =
        {
            "Assets/Scenes/SampleScene.unity"
        };

        string buildKind = isHeadless ? "linux_headless" : "linux_visual";
        string buildId = $"{buildKind}_{TimeStamp()}";
        string buildDir = Path.Combine(BuildOutputRoot(), buildKind, buildId);
        string executableName = isHeadless ? "sample_scene_headless.x86_64" : "sample_scene_visual.x86_64";
        string locationPathName = Path.Combine(buildDir, executableName);

        string gitSha = Environment.GetEnvironmentVariable("UNITY_BUILD_GIT_SHA") ?? "unknown";
        string sceneId = Environment.GetEnvironmentVariable("UNITY_BUILD_SCENE_ID") ?? "unknown";

        EnsureDirectory(buildDir);

        BuildPlayerOptions options = new BuildPlayerOptions
        {
            scenes = scenes,
            locationPathName = locationPathName,
            target = BuildTarget.StandaloneLinux64,
            subtarget = isHeadless ? (int)StandaloneBuildSubtarget.Server : 0,
            options = BuildOptions.StrictMode
        };

        BuildReport report = BuildPipeline.BuildPlayer(options);
        BuildSummary summary = report.summary;

        string metaPath = Path.Combine(buildDir, "build_metadata.txt");
        File.WriteAllText(
            metaPath,
            $"build_id={buildId}\n" +
            $"build_kind={buildKind}\n" +
            $"unity_version={Application.unityVersion}\n" +
            $"git_sha={gitSha}\n" +
            $"scene_id={sceneId}\n" +
            $"timestamp_utc={DateTime.UtcNow:O}\n" +
            $"output={locationPathName}\n" +
            $"result={summary.result}\n" +
            $"total_size={summary.totalSize}\n"
        );

        if (summary.result != BuildResult.Succeeded)
        {
            throw new Exception($"Build failed: {summary.result}");
        }

        Debug.Log($"Build succeeded: {locationPathName}");
    }
}