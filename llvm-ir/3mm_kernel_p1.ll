; ModuleID = '/WAVE/users2/unix/klor/ycho_lab/kimsong_lor/autotuning_tools/experiments/polybench/outputs_kernel_splits/ir/3mm.ll'
source_filename = "/WAVE/users2/unix/klor/ycho_lab/kimsong_lor/autotuning_tools/experiments/polybench/inputs_kernel_splits/linear-algebra/kernels/3mm/3mm.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

; Function Attrs: noinline nounwind optnone uwtable
define hidden void @kernel_p1(i32 %0, i32 %1, i32 %2, [1024 x double]* %3, [1024 x double]* %4, [1024 x double]* %5) #0 !dbg !14 {
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  %10 = alloca [1024 x double]*, align 8
  %11 = alloca [1024 x double]*, align 8
  %12 = alloca [1024 x double]*, align 8
  %13 = alloca i32, align 4
  %14 = alloca i32, align 4
  %15 = alloca i32, align 4
  store i32 %0, i32* %7, align 4
  call void @llvm.dbg.declare(metadata i32* %7, metadata !22, metadata !DIExpression()), !dbg !23
  store i32 %1, i32* %8, align 4
  call void @llvm.dbg.declare(metadata i32* %8, metadata !24, metadata !DIExpression()), !dbg !25
  store i32 %2, i32* %9, align 4
  call void @llvm.dbg.declare(metadata i32* %9, metadata !26, metadata !DIExpression()), !dbg !27
  store [1024 x double]* %3, [1024 x double]** %10, align 8
  call void @llvm.dbg.declare(metadata [1024 x double]** %10, metadata !28, metadata !DIExpression()), !dbg !29
  store [1024 x double]* %4, [1024 x double]** %11, align 8
  call void @llvm.dbg.declare(metadata [1024 x double]** %11, metadata !30, metadata !DIExpression()), !dbg !31
  store [1024 x double]* %5, [1024 x double]** %12, align 8
  call void @llvm.dbg.declare(metadata [1024 x double]** %12, metadata !32, metadata !DIExpression()), !dbg !33
  call void @llvm.dbg.declare(metadata i32* %13, metadata !34, metadata !DIExpression()), !dbg !35
  call void @llvm.dbg.declare(metadata i32* %14, metadata !36, metadata !DIExpression()), !dbg !37
  call void @llvm.dbg.declare(metadata i32* %15, metadata !38, metadata !DIExpression()), !dbg !39
  store i32 0, i32* %13, align 4, !dbg !40
  br label %16, !dbg !42

16:                                               ; preds = %72, %6
  %17 = load i32, i32* %13, align 4, !dbg !43
  %18 = load i32, i32* %7, align 4, !dbg !45
  %19 = icmp slt i32 %17, %18, !dbg !46
  br i1 %19, label %20, label %75, !dbg !47

20:                                               ; preds = %16
  store i32 0, i32* %14, align 4, !dbg !48
  br label %21, !dbg !50

21:                                               ; preds = %68, %20
  %22 = load i32, i32* %14, align 4, !dbg !51
  %23 = load i32, i32* %8, align 4, !dbg !53
  %24 = icmp slt i32 %22, %23, !dbg !54
  br i1 %24, label %25, label %71, !dbg !55

25:                                               ; preds = %21
  %26 = load [1024 x double]*, [1024 x double]** %10, align 8, !dbg !56
  %27 = load i32, i32* %13, align 4, !dbg !58
  %28 = sext i32 %27 to i64, !dbg !56
  %29 = getelementptr inbounds [1024 x double], [1024 x double]* %26, i64 %28, !dbg !56
  %30 = load i32, i32* %14, align 4, !dbg !59
  %31 = sext i32 %30 to i64, !dbg !56
  %32 = getelementptr inbounds [1024 x double], [1024 x double]* %29, i64 0, i64 %31, !dbg !56
  store double 0.000000e+00, double* %32, align 8, !dbg !60
  store i32 0, i32* %15, align 4, !dbg !61
  br label %33, !dbg !63

33:                                               ; preds = %64, %25
  %34 = load i32, i32* %15, align 4, !dbg !64
  %35 = load i32, i32* %9, align 4, !dbg !66
  %36 = icmp slt i32 %34, %35, !dbg !67
  br i1 %36, label %37, label %67, !dbg !68

37:                                               ; preds = %33
  %38 = load [1024 x double]*, [1024 x double]** %11, align 8, !dbg !69
  %39 = load i32, i32* %13, align 4, !dbg !70
  %40 = sext i32 %39 to i64, !dbg !69
  %41 = getelementptr inbounds [1024 x double], [1024 x double]* %38, i64 %40, !dbg !69
  %42 = load i32, i32* %15, align 4, !dbg !71
  %43 = sext i32 %42 to i64, !dbg !69
  %44 = getelementptr inbounds [1024 x double], [1024 x double]* %41, i64 0, i64 %43, !dbg !69
  %45 = load double, double* %44, align 8, !dbg !69
  %46 = load [1024 x double]*, [1024 x double]** %12, align 8, !dbg !72
  %47 = load i32, i32* %15, align 4, !dbg !73
  %48 = sext i32 %47 to i64, !dbg !72
  %49 = getelementptr inbounds [1024 x double], [1024 x double]* %46, i64 %48, !dbg !72
  %50 = load i32, i32* %14, align 4, !dbg !74
  %51 = sext i32 %50 to i64, !dbg !72
  %52 = getelementptr inbounds [1024 x double], [1024 x double]* %49, i64 0, i64 %51, !dbg !72
  %53 = load double, double* %52, align 8, !dbg !72
  %54 = fmul double %45, %53, !dbg !75
  %55 = load [1024 x double]*, [1024 x double]** %10, align 8, !dbg !76
  %56 = load i32, i32* %13, align 4, !dbg !77
  %57 = sext i32 %56 to i64, !dbg !76
  %58 = getelementptr inbounds [1024 x double], [1024 x double]* %55, i64 %57, !dbg !76
  %59 = load i32, i32* %14, align 4, !dbg !78
  %60 = sext i32 %59 to i64, !dbg !76
  %61 = getelementptr inbounds [1024 x double], [1024 x double]* %58, i64 0, i64 %60, !dbg !76
  %62 = load double, double* %61, align 8, !dbg !79
  %63 = fadd double %62, %54, !dbg !79
  store double %63, double* %61, align 8, !dbg !79
  br label %64, !dbg !76

64:                                               ; preds = %37
  %65 = load i32, i32* %15, align 4, !dbg !80
  %66 = add nsw i32 %65, 1, !dbg !80
  store i32 %66, i32* %15, align 4, !dbg !80
  br label %33, !dbg !81, !llvm.loop !82

67:                                               ; preds = %33
  br label %68, !dbg !84

68:                                               ; preds = %67
  %69 = load i32, i32* %14, align 4, !dbg !85
  %70 = add nsw i32 %69, 1, !dbg !85
  store i32 %70, i32* %14, align 4, !dbg !85
  br label %21, !dbg !86, !llvm.loop !87

71:                                               ; preds = %21
  br label %72, !dbg !88

72:                                               ; preds = %71
  %73 = load i32, i32* %13, align 4, !dbg !89
  %74 = add nsw i32 %73, 1, !dbg !89
  store i32 %74, i32* %13, align 4, !dbg !89
  br label %16, !dbg !90, !llvm.loop !91

75:                                               ; preds = %16
  ret void, !dbg !93
}

; Function Attrs: nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

attributes #0 = { noinline nounwind optnone uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { nounwind readnone speculatable willreturn }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!10, !11, !12}
!llvm.ident = !{!13}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "clang version 10.0.1 (https://github.com/conda-forge/clangdev-feedstock 2a1fb6e8a1c6dc6e585535457c24f0295d90c8d2)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !2, retainedTypes: !3, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "/WAVE/users2/unix/klor/ycho_lab/kimsong_lor/autotuning_tools/experiments/polybench/inputs_kernel_splits/linear-algebra/kernels/3mm/3mm.c", directory: "/WAVE/users2/unix/klor/ycho_lab/kimsong_lor/autotuning_tools/scripts")
!2 = !{}
!3 = !{!4, !9, !6}
!4 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !5, size: 64)
!5 = !DICompositeType(tag: DW_TAG_array_type, baseType: !6, size: 67108864, elements: !7)
!6 = !DIBasicType(name: "double", size: 64, encoding: DW_ATE_float)
!7 = !{!8, !8}
!8 = !DISubrange(count: 1024)
!9 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!10 = !{i32 7, !"Dwarf Version", i32 4}
!11 = !{i32 2, !"Debug Info Version", i32 3}
!12 = !{i32 1, !"wchar_size", i32 4}
!13 = !{!"clang version 10.0.1 (https://github.com/conda-forge/clangdev-feedstock 2a1fb6e8a1c6dc6e585535457c24f0295d90c8d2)"}
!14 = distinct !DISubprogram(name: "kernel_p1", scope: !15, file: !15, line: 62, type: !16, scopeLine: 63, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition, unit: !0, retainedNodes: !2)
!15 = !DIFile(filename: "experiments/polybench/inputs_kernel_splits/linear-algebra/kernels/3mm/3mm.c", directory: "/WAVE/users2/unix/klor/ycho_lab/kimsong_lor/autotuning_tools")
!16 = !DISubroutineType(types: !17)
!17 = !{null, !18, !18, !18, !19, !19, !19}
!18 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!19 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !20, size: 64)
!20 = !DICompositeType(tag: DW_TAG_array_type, baseType: !6, size: 65536, elements: !21)
!21 = !{!8}
!22 = !DILocalVariable(name: "ni", arg: 1, scope: !14, file: !15, line: 62, type: !18)
!23 = !DILocation(line: 62, column: 49, scope: !14)
!24 = !DILocalVariable(name: "nj", arg: 2, scope: !14, file: !15, line: 62, type: !18)
!25 = !DILocation(line: 62, column: 57, scope: !14)
!26 = !DILocalVariable(name: "nk", arg: 3, scope: !14, file: !15, line: 62, type: !18)
!27 = !DILocation(line: 62, column: 65, scope: !14)
!28 = !DILocalVariable(name: "E", arg: 4, scope: !14, file: !15, line: 62, type: !19)
!29 = !DILocation(line: 62, column: 79, scope: !14)
!30 = !DILocalVariable(name: "A", arg: 5, scope: !14, file: !15, line: 62, type: !19)
!31 = !DILocation(line: 62, column: 122, scope: !14)
!32 = !DILocalVariable(name: "B", arg: 6, scope: !14, file: !15, line: 62, type: !19)
!33 = !DILocation(line: 62, column: 165, scope: !14)
!34 = !DILocalVariable(name: "i", scope: !14, file: !15, line: 64, type: !18)
!35 = !DILocation(line: 64, column: 7, scope: !14)
!36 = !DILocalVariable(name: "j", scope: !14, file: !15, line: 64, type: !18)
!37 = !DILocation(line: 64, column: 10, scope: !14)
!38 = !DILocalVariable(name: "k", scope: !14, file: !15, line: 64, type: !18)
!39 = !DILocation(line: 64, column: 13, scope: !14)
!40 = !DILocation(line: 66, column: 10, scope: !41)
!41 = distinct !DILexicalBlock(scope: !14, file: !15, line: 66, column: 3)
!42 = !DILocation(line: 66, column: 8, scope: !41)
!43 = !DILocation(line: 66, column: 15, scope: !44)
!44 = distinct !DILexicalBlock(scope: !41, file: !15, line: 66, column: 3)
!45 = !DILocation(line: 66, column: 19, scope: !44)
!46 = !DILocation(line: 66, column: 17, scope: !44)
!47 = !DILocation(line: 66, column: 3, scope: !41)
!48 = !DILocation(line: 67, column: 12, scope: !49)
!49 = distinct !DILexicalBlock(scope: !44, file: !15, line: 67, column: 5)
!50 = !DILocation(line: 67, column: 10, scope: !49)
!51 = !DILocation(line: 67, column: 17, scope: !52)
!52 = distinct !DILexicalBlock(scope: !49, file: !15, line: 67, column: 5)
!53 = !DILocation(line: 67, column: 21, scope: !52)
!54 = !DILocation(line: 67, column: 19, scope: !52)
!55 = !DILocation(line: 67, column: 5, scope: !49)
!56 = !DILocation(line: 69, column: 7, scope: !57)
!57 = distinct !DILexicalBlock(scope: !52, file: !15, line: 68, column: 5)
!58 = !DILocation(line: 69, column: 9, scope: !57)
!59 = !DILocation(line: 69, column: 12, scope: !57)
!60 = !DILocation(line: 69, column: 15, scope: !57)
!61 = !DILocation(line: 70, column: 14, scope: !62)
!62 = distinct !DILexicalBlock(scope: !57, file: !15, line: 70, column: 7)
!63 = !DILocation(line: 70, column: 12, scope: !62)
!64 = !DILocation(line: 70, column: 19, scope: !65)
!65 = distinct !DILexicalBlock(scope: !62, file: !15, line: 70, column: 7)
!66 = !DILocation(line: 70, column: 23, scope: !65)
!67 = !DILocation(line: 70, column: 21, scope: !65)
!68 = !DILocation(line: 70, column: 7, scope: !62)
!69 = !DILocation(line: 71, column: 20, scope: !65)
!70 = !DILocation(line: 71, column: 22, scope: !65)
!71 = !DILocation(line: 71, column: 25, scope: !65)
!72 = !DILocation(line: 71, column: 30, scope: !65)
!73 = !DILocation(line: 71, column: 32, scope: !65)
!74 = !DILocation(line: 71, column: 35, scope: !65)
!75 = !DILocation(line: 71, column: 28, scope: !65)
!76 = !DILocation(line: 71, column: 9, scope: !65)
!77 = !DILocation(line: 71, column: 11, scope: !65)
!78 = !DILocation(line: 71, column: 14, scope: !65)
!79 = !DILocation(line: 71, column: 17, scope: !65)
!80 = !DILocation(line: 70, column: 27, scope: !65)
!81 = !DILocation(line: 70, column: 7, scope: !65)
!82 = distinct !{!82, !68, !83}
!83 = !DILocation(line: 71, column: 36, scope: !62)
!84 = !DILocation(line: 72, column: 5, scope: !57)
!85 = !DILocation(line: 67, column: 26, scope: !52)
!86 = !DILocation(line: 67, column: 5, scope: !52)
!87 = distinct !{!87, !55, !88}
!88 = !DILocation(line: 72, column: 5, scope: !49)
!89 = !DILocation(line: 66, column: 24, scope: !44)
!90 = !DILocation(line: 66, column: 3, scope: !44)
!91 = distinct !{!91, !47, !92}
!92 = !DILocation(line: 72, column: 5, scope: !41)
!93 = !DILocation(line: 73, column: 1, scope: !14)