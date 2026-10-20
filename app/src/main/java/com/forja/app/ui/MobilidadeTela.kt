package com.forja.app.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.forja.app.AppViewModel
import com.forja.app.core.Estado
import com.forja.app.core.Rotina
import com.forja.app.core.Rotinas
import com.forja.app.core.Roteiro

@Composable
fun TelaMobilidade(vm: AppViewModel, estado: Estado, nav: Navegador) {
    var filtro by rememberSaveable { mutableStateOf("Todas") }
    val categorias = listOf("Todas") + Rotinas.CATEGORIAS
    val lista = Rotinas.todas.filter { filtro == "Todas" || it.categoria == filtro }
    val recs = Rotinas.recomendadas(estado.plano?.modalidade, estado.perfil)

    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(bottom = ESPACO_BARRA)) {
        item {
            Column(Modifier.padding(horizontal = 20.dp, vertical = 10.dp)) {
                Rotulo("Alongamento & mobilidade", Cor.modalidade(com.forja.app.core.Modalidade.MOBILIDADE))
                Text("Prepare o corpo,\nrecupere melhor.", style = Tipo.Titulo1, color = Cor.Texto)
                Spacer(Modifier.height(8.dp))
                Text("Antes do esporte, movimento dinâmico. Depois do treino, alongamento estático de 20–30 s. E mobilidade para o dia a dia.", style = Tipo.Corpo, color = Cor.Texto2)
            }
        }
        if (recs.isNotEmpty()) {
            item { Box(Modifier.padding(horizontal = 20.dp)) { Secao("Para o seu treino") } }
            item {
                LazyRow(horizontalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(horizontal = 20.dp)) {
                    items(recs) { r -> CartaoRotinaPequeno(vm, r) { nav.ir(Rota.RotinaDet(r.id)) } }
                }
            }
        }
        item {
            Spacer(Modifier.height(22.dp))
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp), contentPadding = PaddingValues(horizontal = 20.dp)) {
                items(categorias) { c -> Chip(c, c == filtro) { filtro = c } }
            }
            Spacer(Modifier.height(8.dp))
        }
        val grupos = lista.groupBy { it.categoria }
        grupos.forEach { (cat, rs) ->
            item { Box(Modifier.padding(horizontal = 20.dp)) { Secao(cat) } }
            items(rs, key = { it.id }) { r -> LinhaRotina(vm, r, Modifier.padding(horizontal = 20.dp, vertical = 5.dp)) { nav.ir(Rota.RotinaDet(r.id)) } }
        }
    }
}

@Composable
fun Chip(texto: String, sel: Boolean, cor: androidx.compose.ui.graphics.Color = Cor.Brasa, onClick: () -> Unit) {
    val forma = RoundedCornerShape(50)
    Box(
        Modifier.clip(forma).background(if (sel) cor else Cor.Sup1).border(1.dp, if (sel) cor else Cor.Borda, forma)
            .toque(texto + if (sel) ", selecionado" else "", onClick).padding(horizontal = 16.dp, vertical = 9.dp),
    ) { Text(texto, style = Tipo.PequenoForte, color = if (sel) Cor.Fundo else Cor.Texto2, maxLines = 1) }
}

@Composable
private fun LinhaRotina(vm: AppViewModel, r: Rotina, modifier: Modifier, onClick: () -> Unit) {
    val cor = Cor.tema(r.tema)
    val ex = r.sessao.blocos.first().itens.let { it.getOrNull(1) ?: it.first() }.let { vm.catalogo[it.exId] }
    Cartao(modifier.fillMaxWidth(), padding = PaddingValues(12.dp), onClick = onClick, descricao = r.titulo) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            if (ex != null) DemoExercicio(ex, Modifier.size(76.dp), cor = cor, animar = false, cantos = 16.dp)
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(Modifier.size(8.dp).clip(RoundedCornerShape(50)).background(cor))
                    Spacer(Modifier.width(6.dp))
                    Rotulo("${Roteiro.minutos(r.sessao, vm.catalogo)} min · ${r.sessao.blocos.first().itens.size} movimentos", cor)
                }
                Spacer(Modifier.height(3.dp))
                Text(r.titulo, style = Tipo.CorpoForte, color = Cor.Texto, maxLines = 1, overflow = TextOverflow.Ellipsis)
                Text(r.subtitulo, style = Tipo.Pequeno, color = Cor.Texto2, maxLines = 2, overflow = TextOverflow.Ellipsis)
            }
            Icon(Icons.Rounded.ChevronRight, null, tint = Cor.Texto3)
        }
    }
}
