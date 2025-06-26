from llvmlite import binding as llvm
llvm.initialize(); llvm.initialize_native_target()

mod = llvm.parse_assembly(open("kernel.ll").read())

def is_load_or_store(inst):
    return inst.opcode in ('load', 'store')

def bytes_of_access(inst, dl):
    ty = inst.type.pointee if inst.opcode=='load' else inst.operands[0].type.pointee
    return dl.getTypeAllocSize(ty)

dl = llvm.create_target_machine().target_data
stats = {'loads':0, 'stores':0, 'bytes':0, 'atomic':0, 'barrier':0}

for fn in mod.functions:
    if fn.name.startswith('.omp_outlined'):
        for bb in fn.basic_blocks:
            for inst in bb.instructions:
                if is_load_or_store(inst):
                    stats[inst.opcode+'s'] += 1
                    stats['bytes']        += bytes_of_access(inst, dl)
                elif inst.opcode in ('atomicrmw','cmpxchg'):
                    stats['atomic'] += 1
                elif getattr(inst, 'called_function', None) and \
                     inst.called_function.name.startswith('__kmpc_barrier'):
                    stats['barrier'] += 1

print(stats)
